import gnupg
import gzip
import shutil


def compress_file(filename_in, filename_out):
    with open(filename_in, 'rb') as f_in:
        with gzip.open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def uncompress_file(filename_in, filename_out):
    with gzip.open(filename_in, 'rb') as f_in:
        with open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def encrypt_file(filename_in, filename_out):
    gpg = gnupg.GPG(gnupghome='.')
    gpg.encoding = 'utf-8'
    with open(filename_in, "rb") as f:
        gpg.encrypt_file(f, None, symmetric=True, passphrase='poops', output=filename_out)


def decrypt_file(filename_in, filename_out):
    gpg = gnupg.GPG(gnupghome='.')
    gpg.encoding = 'utf-8'
    with open(filename_in, "rb") as f:
        gpg.decrypt_file(f, passphrase='poops', output=filename_out)
