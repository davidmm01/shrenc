import filecmp
import os
import shutil

import pytest

from app.operations import (
    decrypt_file,
    encrypt_file,
    tar_and_compress,
    undo_tar_and_compress,
)


@pytest.mark.parametrize("compression", ["tar_only", "gzip", "bz2", "lzma"])
def test_file_compression_and_extraction_on_single_file(compression):
    TEST_FILE = "some_file.txt"
    COMPRESSED_NAME_WO_EXT = "new_archive"
    UNCOMPRESSED_FILE_DEST = "archive_undo"

    # TODO: a real nice cleanup function
    # for path in (TEST_FILE, COMPRESSED_NAME_WO_EXT, UNCOMPRESSED_FILE_DEST):
    #     if os.path.exists(path):
    #         os.remove(path)

    # Make a test file
    with open(TEST_FILE, "w") as f:
        f.write("blahhhhhhh")

    # compress the file and check the file exists
    filename = tar_and_compress(TEST_FILE, COMPRESSED_NAME_WO_EXT, compression)
    assert os.path.exists(filename)

    # uncompress the file and check the file exists
    undo_tar_and_compress(filename, UNCOMPRESSED_FILE_DEST)
    uncompress_expected_path = f"{UNCOMPRESSED_FILE_DEST}/{TEST_FILE}"
    assert os.path.exists(uncompress_expected_path)

    # check file looks the same before and after compression
    assert filecmp.cmp(TEST_FILE, uncompress_expected_path)

    # cleanup
    os.remove(TEST_FILE)
    os.remove(filename)
    shutil.rmtree(UNCOMPRESSED_FILE_DEST)


def test_file_encryption_and_decryption():
    TEST_FILE = "some_file.txt"
    ENCRYPTED_FILE = "some_file_enc"
    DECRYPTED_FILE = "some_file_dec.txt"

    # Make a test file
    with open(TEST_FILE, "w") as f:
        f.write("blahhhhhhh")

    # encrypt the test file and check the file exists
    encrypt_file(TEST_FILE, ENCRYPTED_FILE, "poops")
    assert os.path.exists(ENCRYPTED_FILE)

    # compare the standard and encrypt files, the content should be different
    assert not filecmp.cmp(TEST_FILE, ENCRYPTED_FILE)

    # check contents looks the same before and after decrypting
    decrypt_file(ENCRYPTED_FILE, DECRYPTED_FILE, "poops")
    assert os.path.exists(DECRYPTED_FILE)
    assert filecmp.cmp(TEST_FILE, DECRYPTED_FILE)

    # cleanup
    for file_ in (TEST_FILE, ENCRYPTED_FILE, DECRYPTED_FILE):
        os.remove(file_)


# TODO: add a test where mismatched passphrases are passed?
