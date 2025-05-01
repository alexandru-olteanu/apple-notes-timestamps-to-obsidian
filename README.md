# apple-notes-timestamps-to-obsidian

Inject **Created at/Updated at** timestamps from Apple Notes into your Obsidian-imported
notes as YAML front-matter.

## Requirements

* macOS (needs AppleScript access to the Notes app)
* Python 3+
* Obsidian vault that contains the Markdown files exported by [**Obsidian Importer**](https://help.obsidian.md/import/apple-notes)

## Clone repo

```bash
git clone <this-repo>
cd apple-notes-timestamps-to-obsidian
```

## Usage

### Step 1: Import your notes from Apple Notes

Use [**Obsidian Importer**](https://help.obsidian.md/import/apple-notes) to import Apple Notes into an Obsidian vault.

### Step 2: Run the script

Replace `/path/to/your/obsidian/vault` with the actual path to your Obsidian vault directory that contains the Markdown files imported from Apple Notes.

```bash
python main.py "/path/to/your/obsidian/vault/Apple Notes"
```

The script will:

1. Run the `get_notes` AppleScript to extract creation and modification timestamps.
2. Cache them locally in `apple_notes_timestamps.json`.
3. Iterate over all `.md` files in your Obsidian vault.
4. Inject the following front matter at the top of each file (if not already present):

```
---
Created at: 2024-01-01T10:00:00+02:00
Updated at: 2024-02-01T15:42:00+02:00
---
```

## Notes

- Files that already contain front matter (`---` at the top) will be skipped.
- If the cache (`apple_notes_timestamps.json`) already exists, it will be reused to avoid running AppleScript again.
- Paths are sanitized to match how [Obsidian Importer](https://github.com/obsidianmd/obsidian-importer/blob/b14b3ae79a278f0402f7bc5bd5f0b5152406aeb5/src/util.ts#L11) names files.

## Example

```bash
python main.py "/Users/yourname/Library/Mobile Documents/iCloud~md~obsidian/Documents/AwesomeVault/Apple Notes"
```

---

Enjoy timestamp-accurate journaling in Obsidian!
