from datetime import datetime
from main import AppleNotesTimestampsInjector  # replace 'your_module' with the actual module filename

def test_parse_apple_date_basic():
    input_date = "Saturday, 26 April 2025 at 08:34:39"
    result = AppleNotesTimestampsInjector.parse_apple_date(input_date)

    # Parse again to validate it's a proper ISO string
    parsed = datetime.fromisoformat(result)
    assert parsed.year == 2025
    assert parsed.month == 4
    assert parsed.day == 26
    assert parsed.hour == 8 or parsed.utcoffset() is not None  # handle local time

def test_parse_apple_date_format():
    input_date = "Monday, 01 January 2024 at 00:00:00"
    result = AppleNotesTimestampsInjector.parse_apple_date(input_date)

    # Should be a valid ISO 8601 format with time and offset
    assert "T00:00:00" in result
    assert "+" in result or "-" in result in "Z" in result  # timezone info must be there
