import filecmp
import os

from app.operations import compress_file, decrypt_file, encrypt_file, uncompress_file


def test_file_compression_and_extraction():
    TEST_FILE = "some_file.txt"
    COMPRESSED_TEST_FILE = "some_file.tgz"
    UNCOMPRESSED_TEST_FILE = "some_file_uncompressed.txt"

    # start from clean
    for file_ in (TEST_FILE, COMPRESSED_TEST_FILE, UNCOMPRESSED_TEST_FILE):
        if os.path.exists(file_):
            os.remove(file_)

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
    assert filecmp.cmp(TEST_FILE, UNCOMPRESSED_TEST_FILE)

    # cleanup
    for file_ in (TEST_FILE, COMPRESSED_TEST_FILE, UNCOMPRESSED_TEST_FILE):
        os.remove(file_)


def test_file_encryption_and_decryption():
    TEST_FILE = "some_file.txt"
    ENCRYPTED_FILE = "some_file_enc"
    DECRYPTED_FILE = "some_file_dec.txt"

    # Make a test file
    with open(TEST_FILE, "w") as f:
        f.write("blahhhhhhh")

    # encrypt the test file and check the file exists
    encrypt_file(TEST_FILE, ENCRYPTED_FILE)
    assert os.path.exists(ENCRYPTED_FILE)

    # compare the standard and encrypt files, the content should be different
    assert not filecmp.cmp(TEST_FILE, ENCRYPTED_FILE)

    # check contents looks the same before and after decrypting
    decrypt_file(ENCRYPTED_FILE, DECRYPTED_FILE)
    assert os.path.exists(DECRYPTED_FILE)
    assert filecmp.cmp(TEST_FILE, DECRYPTED_FILE)

    # cleanup
    for file_ in (TEST_FILE, ENCRYPTED_FILE, DECRYPTED_FILE):
        os.remove(file_)
