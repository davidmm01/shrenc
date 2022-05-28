import filecmp
import os

from app.operations import compress_file, uncompress_file


def test_file_compression_and_extraction():
    # start from clean
    for file_ in (TEST_FILE, COMPRESSED_TEST_FILE, UNCOMPRESSED_TEST_FILE):
        if os.path.exists(file_):
            os.remove(file_)

    TEST_FILE = "some_file.txt"
    COMPRESSED_TEST_FILE = "some_file.tgz"
    UNCOMPRESSED_TEST_FILE = "some_file_uncompressed.txt"

    # Make a test file
    with open(TEST_FILE, "w") as f:
        f.write("blahhhhhhh")

    # compress the file and check the file exists
    compress_file(TEST_FILE, COMPRESSED_TEST_FILE)
    assert os.path.exists(COMPRESSED_TEST_FILE)

    # uncompress the file and check the file exists
    uncompress_file(COMPRESSED_TEST_FILE, UNCOMPRESSED_TEST_FILE)
    assert os.path.exists(UNCOMPRESSED_TEST_FILE)

    # check file looks the same before and after compression
    filecmp.cmp(TEST_FILE, UNCOMPRESSED_TEST_FILE)

    # cleanup
    for file_ in (TEST_FILE, COMPRESSED_TEST_FILE, UNCOMPRESSED_TEST_FILE):
        os.remove(file_)
