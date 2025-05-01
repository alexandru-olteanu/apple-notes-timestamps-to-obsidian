import argparse
import os
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d %(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

TIMESTAMPS_FILE = "apple_notes_timestamps.json"
ICLOUD_PREFIX = "iCloud/"
DELIMITER = "|{|}|"


class AppleNotesTimestampsInjector:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    def get_apple_notes_timestamps(self) -> Dict[str, Dict[str, str]]:
        """Get Apple Notes timestamps either from cache or by running AppleScript."""
        timestamps_file = os.path.join(os.path.dirname(__file__), TIMESTAMPS_FILE)
        
        # Try to load from cache first
        if os.path.exists(timestamps_file):
            logger.info(f"Loading timestamps from {TIMESTAMPS_FILE}")
            with open(timestamps_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # If cache doesn't exist, run AppleScript
        logger.info("Cache with timestamps not found. Running AppleScript to get timestamps...")
        return self._extract_timestamps_from_applescript()

    def _extract_timestamps_from_applescript(self) -> Dict[str, Dict[str, str]]:
        """Run AppleScript to extract note timestamps."""
        script_path = os.path.join(os.path.dirname(__file__), "get_notes.applescript")
        
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True, text=True
        )

        if result.stderr:
            logger.warning(f"AppleScript error: {result.stderr}")

        notes = {}
        for line in result.stdout.strip().split("\n"):
            if DELIMITER in line:
                note_path, created, updated = line.split(DELIMITER)
                # Remove iCloud prefix before saving 
                note_path = note_path.strip().removeprefix(ICLOUD_PREFIX)
                # Remove special chars from path because Importer also did that
                # https://github.com/obsidianmd/obsidian-importer/blob/b14b3ae79a278f0402f7bc5bd5f0b5152406aeb5/src/util.ts#L11
                note_path = self.sanitize_file_name(note_path)
                notes[note_path] = {
                    "created": self.parse_apple_date(created.strip()),
                    "updated": self.parse_apple_date(updated.strip())
                }
        
        # Save the extracted timestamps to cache
        self.save_apple_notes_timestamps(notes)
        return notes

    @staticmethod
    def sanitize_file_name(name: str) -> str:
        illegal_re = re.compile(r'[\?<>\\:\*\|"]')  # Removed / from illegal chars
        control_re = re.compile(r'[\x00-\x1f\x80-\x9f]')
        reserved_re = re.compile(r'^\.+$')
        windows_reserved_re = re.compile(r'^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?$', re.IGNORECASE)
        windows_trailing_re = re.compile(r'[\. ]+$')
        starts_with_dot_re = re.compile(r'^\.+')
        bad_link_re = re.compile(r'[\[\]#\|\^]')

        name = illegal_re.sub('', name)
        name = control_re.sub('', name)
        name = reserved_re.sub('', name)
        name = windows_reserved_re.sub('', name)
        name = windows_trailing_re.sub('', name)
        name = starts_with_dot_re.sub('', name)
        name = bad_link_re.sub('', name)

        return name

    @staticmethod
    def parse_apple_date(date_str: str) -> str:
        """Parse AppleScript date string into ISO format."""
        # AppleScript returns something like: "Saturday, 26 April 2025 at 08:34:39"
        dt = datetime.strptime(date_str, "%A, %d %B %Y at %H:%M:%S")
        return dt.astimezone().isoformat(timespec='seconds')

    def inject_front_matter(self, filepath: Path, created: str, updated: str) -> bool:
        """Inject front matter into a markdown file if it doesn't already have it."""
        relative_path = filepath.relative_to(self.vault_path)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith("---\n"):
            logger.warning(f'"{relative_path}" already has front matter. Skipping')
            return False

        fm_text = f"---\nCreated at: {created}\nUpdated at: {updated}\n---\n"
        new_content = fm_text + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logger.info(f'Added front matter to "{relative_path}"')
        return True

    def process_obsidian_notes(self, apple_notes_timestamps: Dict[str, Dict[str, str]]) -> None:
        """Process Obsidian notes and inject front matter with timestamps."""
        obsidian_total_count = 0 
        obsidian_not_found = 0
        obsidian_added = 0
        obsidian_skipped = 0
        for md_file in Path(self.vault_path).rglob("*.md"):
            obsidian_total_count += 1
            rel_path = md_file.relative_to(self.vault_path)
            note_path = str(rel_path.with_suffix(''))
            
            if note_path in apple_notes_timestamps:
                timestamps = apple_notes_timestamps[note_path]
                logger.info(f"Processing \"{rel_path}\": created={timestamps['created']}, updated={timestamps['updated']}")
                if self.inject_front_matter(md_file, timestamps["created"], timestamps["updated"]):
                    obsidian_added += 1
                else:
                    obsidian_skipped += 1
            else:
                obsidian_not_found += 1
                logger.warning(f"Apple Note not found for {rel_path}")
        
        logger.info(f"obsidian_total_count: {obsidian_total_count}")
        logger.info(f"obsidian_not_found: {obsidian_not_found}")
        logger.info(f"obsidian_added: {obsidian_added}")
        logger.info(f"obsidian_skipped: {obsidian_skipped}")

    def save_apple_notes_timestamps(self, apple_notes: Dict[str, Dict[str, str]]) -> None:
        """Save Apple Notes timestamps to a JSON file."""
        output_path = os.path.join(os.path.dirname(__file__), TIMESTAMPS_FILE)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(apple_notes, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(apple_notes)} notes to {TIMESTAMPS_FILE}")

    def run(self):
        apple_notes_timestamps = self.get_apple_notes_timestamps()
        apple_notes_count = len(apple_notes_timestamps)
        logger.info(f"Processing {apple_notes_count} notes from Apple Notes...")
        self.process_obsidian_notes(apple_notes_timestamps)
        logger.info(f"apple_notes_count = {apple_notes_count}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Add Created at/Updated at YAML front‑matter to Obsidian‑imported Apple Notes."
    )
    parser.add_argument(
        "vault_path",
        nargs="?",
        help="Path to the Obsidian vault",
    )
    return parser.parse_args()


def main() -> None:
    """Main function to orchestrate the process."""
    args = parse_args()
    processor = AppleNotesTimestampsInjector(args.vault_path)
    processor.run()

if __name__ == "__main__":
    main()
