import bz2
import gnupg
import gzip
import lzma
import shutil

# TODO: we can probs add a bunch of options andd stuff to these compressions, and
# if not, then refactor and stop having so much duplication?

# TODO: rename this fella so its clear its about gzip
def compress_file_gzip(filename_in, filename_out):
    with open(filename_in, 'rb') as f_in:
        with gzip.open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def uncompress_file_gzip(filename_in, filename_out):
    with gzip.open(filename_in, 'rb') as f_in:
        with open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def compress_file_lzma(filename_in, filename_out):
    with open(filename_in, 'rb') as f_in:
        with lzma.open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def uncompress_file_lzma(filename_in, filename_out):
    with lzma.open(filename_in, 'rb') as f_in:
        with open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def compress_file_bz2(filename_in, filename_out):
    with open(filename_in, 'rb') as f_in:
        with bz2.open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def uncompress_file_bz2(filename_in, filename_out):
    with bz2.open(filename_in, 'rb') as f_in:
        with open(filename_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def encrypt_file(filename_in, filename_out, symmetric=True, armor=True):
    # TODO: now that we always pass armor and symmetric, can remove the defaults
    gpg = gnupg.GPG(gnupghome='.')
    gpg.encoding = 'utf-8'
    with open(filename_in, "rb") as f:
        gpg.encrypt_file(
            f,
            None,
            symmetric=symmetric,
            passphrase='poops',
            output=filename_out,
            armor=armor,
        )


def decrypt_file(filename_in, filename_out):
    gpg = gnupg.GPG(gnupghome='.')
    gpg.encoding = 'utf-8'
    with open(filename_in, "rb") as f:
        gpg.decrypt_file(f, passphrase='poops', output=filename_out)
