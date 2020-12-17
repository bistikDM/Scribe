import os
from pathlib import Path
from typing import Union, Tuple, List

import tqdm


def copy_files(file_name: Union[Tuple[str, str], List[Tuple[str, str]]], destination_directory: str):
    """
    Copies file(s) to the provided destination.

    :param file_name: The file(s) in (section name, absolute path) tuple pair to be copied.
    :param destination_directory: The location where the file(s) will be copied to.
    :return: True if the operation was successful, otherwise false.
    """
    # Create the directories if it does not exist.
    if not Path(destination_directory).exists():
        os.makedirs(destination_directory)

    if isinstance(file_name, List):
        for file in file_name:
            # Create the final destination directories that mirrors the repository then copy files.
            final_path = str(os.path.join(destination_directory, file[0]))
            if not Path(final_path).exists():
                os.makedirs(final_path)
            head_tail = os.path.split(file[1])
            destination = os.path.join(final_path, head_tail[1])
            __copy(file[1], destination)
    else:
        # Create the final destination directories that mirrors the repository then copy file.
        final_path = str(os.path.join(destination_directory, file_name[0]))
        if not Path(final_path).exists():
            os.makedirs(final_path)
        head_tail = os.path.split(file_name[1])
        destination = os.path.join(final_path, head_tail[1])
        __copy(file_name[1], destination)


def __copy(src: str, dst: str):
    # https://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast
    # shutil library reported to be slow for windows based system because of limited buffer size.
    try:
        o_binary = os.O_BINARY
    except os.error:
        # Not running on Windows.
        o_binary = 0
    read_flags = os.O_RDONLY | o_binary
    write_flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | o_binary
    buffer_size = 128 * 1024
    try:
        file_in = os.open(src, read_flags)
        stat = os.fstat(file_in)
        file_out = os.open(dst, write_flags, stat.st_mode)
        with tqdm.tqdm(desc=os.path.split(src)[1], total=stat.st_size, unit_scale=True, unit="") as bar:
            for x in iter(lambda: os.read(file_in, buffer_size), b''):
                os.write(file_out, x)
                bar.update(len(x))
    except os.error:
        print("Copy failed for %s!" % src)
    finally:
        try:
            os.close(file_in)
        except os.error:
            # Failed to close file.
            # TODO: Error logging.
            pass
        try:
            os.close(file_out)
        except os.error:
            # Failed to close file.
            # TODO: Error logging.
            pass
