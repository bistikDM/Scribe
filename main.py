import configparser
import os
import shutil
from pathlib import Path
from typing import Union, List, Dict

base_config = "config.ini"
home = str(os.path.expanduser("~"))
root_directory = str(os.path.join(home, "file-picker"))
base_paths = {"host_1": str(os.path.join(home, "host_1")),
              "host_2": str(os.path.join(home, "host_2")),
              "host_3": str(os.path.join(home, "host_3")),
              "host_4": str(os.path.join(home, "host_4")),
              "guide": str(os.path.join(home, "guide"))}

# TODO: Remove this variable!
test_build = {"host_1": "test_1.1, test_1.2, test_1.3",
              "host_2": "test_2",
              "host_3": "test_3",
              "host_4": "test_4",
              "host_5_does_not_exist": "does_not_exist",
              "guide": "test_guide_directory"}


def create_config(absolute_path: str,
                  fname: str = base_config,
                  configuration: Dict = None) -> str:
    """
    Creates a configuration file to be used.

    :param absolute_path: The location the file will be created.
    :param fname: The name of the configuration file.
    :param configuration: The configuration to be entered into the file.
    :return: The newly created configuration file's path.
    """
    print("Creating base config file.")

    # Use default dictionary if none is given.
    if configuration is None:
        configuration = base_paths

    # Create the directories if it does not exist.
    if not Path(absolute_path).exists():
        os.makedirs(absolute_path)
    config = configparser.ConfigParser()
    config["DEFAULT"] = configuration

    # TODO: Remove this line!
    config["test_build"] = test_build

    # Write the configuration into the file.
    with open(os.path.join(absolute_path, fname), "w") as config_file:
        config.write(config_file)
        config_file.close()
        print("Base config file created.")

    return os.path.join(absolute_path, fname)


def get_config(absolute_path: str = root_directory, fname: str = base_config) -> str:
    """
    Retrieves the configuration file path needed.

    :param absolute_path: The path to the configuration file.
    :param fname: The name of the configuration file.
    :return: The configuration file path.
    """
    config_file = Path(str(os.path.join(absolute_path, fname)))

    # Create a new configuration file if it does not exist.
    if not config_file.exists():
        config_file = create_config(absolute_path)

    return config_file


def select_build(fname: str) -> List[str]:
    """
    Reads, display, then allow the selection of a specific build from the configuration file.

    :param fname: The configuration file.
    :return: A list of file paths for the associated build.
    """
    config = configparser.ConfigParser()
    config.read(fname)
    sections = config.sections()
    print("Build list:")

    for section in sections:
        print("\t", str((sections.index(section) + 1)) + ").".ljust(5), section)

    index = None

    # Get user's selection.
    while not index:
        index = int(input("Enter a build number: "))
        if index < len(sections) or index > len(sections):
            index = None
            print("Invalid selection!")

    selection = sections[index - 1]
    print("\nBuild", selection, "selected:")
    subsection = config[selection]
    files = []
    skipped_hosts = {}

    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in subsection:
        text = entry
        if len(text) > 20:
            text = entry[:17] + "..."
        print("\t", text.ljust(20), "=", subsection[entry])

        # The files are in a csv format while the guide will be a whole directory containing multiple documents.
        if "guide" not in entry:
            images = config[selection][entry].split(",")
            for image in images:
                if config.has_option("DEFAULT", entry):
                    path = os.path.join(config["DEFAULT"][entry], image.strip())
                    files.append(path)
                else:
                    skipped_hosts[entry] = config[selection][entry]
        else:
            if config.has_option("DEFAULT", entry):
                path = os.path.join(config["DEFAULT"][entry], config[selection][entry])
                files.append(path)
            else:
                skipped_hosts[entry] = config[selection][entry]

    if skipped_hosts:
        print("\n*WARNING* Path does not exist in \"DEFAULT\" for the following host(s), and has been skipped:")
        for entry in skipped_hosts:
            text = entry
            if len(text) > 20:
                text = entry[:17] + "..."
            print("\t", text.ljust(20), "=", skipped_hosts[entry])
        print("\n")

    return files


def add_new_build(fname: str = base_config):
    """
    Add a new build configuration.

    :param fname: The configuration file to save into.
    """
    config = configparser.ConfigParser()
    config.read(fname)

    while True:
        build_title = input("Please enter a build name: ")
        if not config.has_section(build_title):
            break
        print("The build name already exist!")
    build_options = __create_dict(fname)
    print("Saving [%s] into the config file..." % build_title)
    with open(os.path.join(fname), "a") as config_file:
        config = configparser.ConfigParser()
        config.add_section(build_title)
        config[build_title] = build_options
        config.write(config_file)
        config_file.close()
        print("New build configuration saved.")


def __create_dict(fname: str) -> Dict[str, str]:
    """
    Create a dictionary from user's input.

    :param fname: The configuration file to get the "DEFAULT" section for keys.
    :return: A dictionary based on "DEFAULT" section and user's input.
    """
    config = configparser.ConfigParser()
    config.read(fname)
    default = config["DEFAULT"]
    new_build = {}
    confirm = False
    print("\n*Enter either a comma separated value of multiple image files or a single image file*")

    while not confirm:
        for key in default:
            if "guide" not in key:
                entry = input("Please enter value for the host %s: " % key)
                new_build[key] = entry
        for entry in new_build:
            text = entry
            if len(text) > 20:
                text = entry[:17] + "..."
            print("\t", text.ljust(20), "=", new_build[entry])
        print("\n")
        selection = input("Enter 'y/Y' to confirm entries: ")
        if selection in ["y", "Y"]:
            confirm = True

    return new_build


def remove_build(fname: str):
    # TODO
    pass


def edit_build(fname: str):
    # TODO
    pass


def cherry_pick(fname: str):
    # TODO: Allow user to pick a certain option from a section to copy.
    pass


def print_storage():
    # TODO: display the tree of the "image repo" and its content.
    pass


def copy_files(fname: Union[str, List[str]], dest_dir: str):
    """
    Copies file(s) to the provided destination.

    :param fname: The file(s) to be copied.
    :param dest_dir: The location where the file(s) will be copied to.
    :return: True if the operation was successful, otherwise false.
    """
    # Create the directories if it does not exist.
    if not Path(dest_dir).exists():
        os.makedirs(dest_dir)

    if isinstance(fname, List):
        for file in fname:
            head_tail = os.path.split(file)
            dest = os.path.join(dest_dir, head_tail[1])
            __copy(file, dest)
    else:
        head_tail = os.path.split(fname)
        dest = os.path.join(dest_dir, head_tail[1])
        __copy(fname, dest)


def __copy(src: str, dst: str):
    # https://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast
    # shutil library reported to be slow for windows based system because of limited buffer size.
    try:
        O_BINARY = os.O_BINARY
    except:
        O_BINARY = 0
    READ_FLAGS = os.O_RDONLY | O_BINARY
    WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
    BUFFER_SIZE = 128 * 1024
    try:
        fin = os.open(src, READ_FLAGS)
        stat = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
        for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
            os.write(fout, x)
    except:
        print("Copy failed for %s!" % src)
    finally:
        try:
            os.close(fin)
        except:
            pass
        try:
            os.close(fout)
        except:
            pass


def main():
    # TESTING
    test_file = get_config()
    print("Test file:", test_file)
    confirm = False
    while not confirm:
        files = select_build(test_file)
        selection = input("Enter 'y/Y' to confirm selection: ")
        if selection in ["y", "Y"]:
            confirm = True
    for file in files:
        print(file)
    # copy_files(files, str(os.path.join(home, "file-picker")))
    shutil.rmtree(str(os.path.join(home, "file-picker")))


if __name__ == "__main__":
    main()
