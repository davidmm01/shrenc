import tarfile

import gnupg

EXT_TAR = ".tar"
EXT_BZ2 = ".bz2"
EXT_TAR_BZ2 = EXT_TAR + EXT_BZ2
EXT_GZIP = ".gz"
EXT_TAR_GZIP = EXT_TAR + EXT_GZIP
EXT_LZMA = ".xz"
EXT_TAR_LZMA = EXT_TAR + EXT_LZMA

PARAM_TO_TAR_COMPRESS_SETTINGS = {
    "tar_only": {"mode": "w", "ext": EXT_TAR},
    "gzip": {"mode": "w:gz", "ext": EXT_TAR_GZIP},
    "bz2": {"mode": "w:bz2", "ext": EXT_TAR_BZ2},
    "lzma": {"mode": "w:xz", "ext": EXT_TAR_LZMA},
}

EXT_TO_MODE = {
    EXT_TAR: "r:",
    EXT_TAR_GZIP: "r:gz",
    EXT_TAR_BZ2: "r:bz2",
    EXT_TAR_LZMA: "r:xz",
}


def tar_and_compress(path, archive_name, compression="no-compression"):
    settings = PARAM_TO_TAR_COMPRESS_SETTINGS.get(compression)
    if not settings:
        # TODO: raise suitable error here, and a unit test for this
        pass

    output_name = archive_name + settings["ext"]
    mode = settings["mode"]

    with tarfile.open(output_name, mode) as tar:
        tar.add(path)

    return output_name


def undo_tar_and_compress(archive, dest="."):
    mode = None
    for key in EXT_TO_MODE:
        if archive.endswith(key):
            mode = EXT_TO_MODE[key]
            continue

    if not mode:
        # TODO: raise suitable error here, and a unit test for this
        pass

    with tarfile.open(archive, mode) as tar:
        tar.extractall(dest)


def encrypt_file(filename_in, filename_out, passphrase, symmetric=True, armor=True):
    # TODO: now that we always pass armor and symmetric, can remove the defaults
    gpg = gnupg.GPG(gnupghome=".")
    gpg.encoding = "utf-8"
    with open(filename_in, "rb") as f:
        gpg.encrypt_file(
            f,
            None,
            symmetric=symmetric,
            passphrase=passphrase,
            output=filename_out,
            armor=armor,
        )


def decrypt_file(filename_in, filename_out, passphrase):
    gpg = gnupg.GPG(gnupghome=".")
    gpg.encoding = "utf-8"
    with open(filename_in, "rb") as f:
        gpg.decrypt_file(f, passphrase=passphrase, output=filename_out)
