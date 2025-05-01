
from main import AppleNotesTimestampsInjector


def test_illegal_chars():
    """Test removal of illegal characters"""
    assert AppleNotesTimestampsInjector.sanitize_file_name("test?file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test<file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test>file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test\\file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test:file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test*file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test|file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name('test"file') == "testfile"

def test_control_chars():
    """Test removal of control characters"""
    assert AppleNotesTimestampsInjector.sanitize_file_name("test\x00file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test\x1ffile") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test\x80file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test\x9ffile") == "testfile"

def test_reserved_names():
    """Test handling of reserved names"""
    assert AppleNotesTimestampsInjector.sanitize_file_name(".") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("..") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("...") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("con") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("CON") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("con.txt") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("prn") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("aux") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("nul") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("com1") == ""
    assert AppleNotesTimestampsInjector.sanitize_file_name("lpt1") == ""

def test_trailing_chars():
    """Test removal of trailing dots and spaces"""
    assert AppleNotesTimestampsInjector.sanitize_file_name("test.") == "test"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test..") == "test"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test ") == "test"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test  ") == "test"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test . ") == "test"

def test_starts_with_dot():
    """Test handling of names starting with dot"""
    assert AppleNotesTimestampsInjector.sanitize_file_name(".test") == "test"
    assert AppleNotesTimestampsInjector.sanitize_file_name("..test") == "test"
    assert AppleNotesTimestampsInjector.sanitize_file_name("...test") == "test"

def test_bad_link_chars():
    """Test removal of bad link characters"""
    assert AppleNotesTimestampsInjector.sanitize_file_name("test[file]") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test#file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test|file") == "testfile"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test^file") == "testfile"

def test_combined_cases():
    """Test combined cases with multiple issues"""
    assert AppleNotesTimestampsInjector.sanitize_file_name(".test?file[1].txt") == "testfile1.txt"
    assert AppleNotesTimestampsInjector.sanitize_file_name("?file.txt") == "file.txt"
    assert AppleNotesTimestampsInjector.sanitize_file_name("test\x00file.txt.") == "testfile.txt"
    assert AppleNotesTimestampsInjector.sanitize_file_name("..test?file[1].txt ") == "testfile1.txt"
    assert AppleNotesTimestampsInjector.sanitize_file_name("..test?file[1]..txt ") == "testfile1..txt"
    assert AppleNotesTimestampsInjector.sanitize_file_name("..test?file[1]..") == "testfile1"
