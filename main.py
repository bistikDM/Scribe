import configparser
import os
import random
import shutil
from pathlib import Path
from typing import Union, List, Dict, Tuple

import tqdm

base_config_name = "config.ini"
file_list_config_name = "file-list.ini"
home = str(os.path.expanduser("~"))
root_directory = str(os.path.join(home, "file-picker"))
base_paths = {"file_list": str(os.path.join(home, "file-picker", file_list_config_name))}

CONFIGURATION = "CONFIGURATION"
HOST_NAMES = "HOST_NAMES"

file_list_default = {"base_directory": "file-picker-dev1, file-picker-dev2, file-picker-dev3",
                     "firmware_directory": "firmware",
                     "network_directory": "network",
                     "images_directory": "volume",
                     "iso_directory": "ISO_images",
                     "config_directory": "configs",
                     "delta_directory:": "deltas",
                     "tools_directory": "tools"}

default_host_names = {"firmware": "True",
                      "network": "True",
                      "volume": "True",
                      "ISO_images": "True",
                      "configs": "True",
                      "deltas": "True",
                      "tools": "True"}

# TODO: Remove this variable!
test_build = {"firmware": "test_1.1, test_1.2, test_1.3",
              "network": "test_2",
              "volume": "test_3",
              "ISO_images": "test_4",
              "configs": "test_5",
              "deltas": "test_6",
              "tools": "install, test, misc"}


def __create_config(absolute_path: str, file_name: str = base_config_name, configuration: Dict = None,
                    host_names: Dict = None) -> str:
    """
    Creates a configuration file to be used.

    :param absolute_path: The location the file will be created.
    :param file_name: The name of the configuration file.
    :param configuration: The configuration to be entered into the file.
    :param host_names: The default host names to use.
    :return: The newly created configuration file's path.
    """
    print("Creating base config file.")

    # Use default dictionary if none is given.
    if configuration is None:
        configuration = base_paths

    if host_names is None:
        host_names = default_host_names

    # Create the directories if it does not exist.
    if not Path(absolute_path).exists():
        os.makedirs(absolute_path)
    config = configparser.ConfigParser()
    config[CONFIGURATION] = configuration
    config[HOST_NAMES] = host_names

    # TODO: Remove this line!
    config["test_build"] = test_build

    # Write the configuration into the file.
    with open(os.path.join(absolute_path, file_name), "w") as config_file:
        config.write(config_file)
        config_file.close()
        print("Base config file created.")

    # Create a new file list if it does not exist.
    file_list_config_file = Path(str(os.path.join(absolute_path, file_list_config_name)))
    if not file_list_config_file.exists():
        __create_file_list_config(absolute_path)

    return os.path.join(absolute_path, file_name)


def __create_file_list_config(absolute_path: str, file_name: str = file_list_config_name):
    """
    Creates a configuration file that contains a listing of all available files within the system.

    :param absolute_path: The location the file will be created.
    :param file_name: The name of the configuration file.
    """
    config = configparser.ConfigParser()
    config[CONFIGURATION] = file_list_default
    print("Discovering files, this may take a while...")

    # Crawling block.
    # Iterate over a list created out of the base_directory option.
    for base in map(lambda x: x.strip(), config.get(CONFIGURATION, "base_directory").split(",")):
        os_root_and_base = os.path.join(os.path.abspath(os.sep), base)
        # Start crawling from the root directory + base, / for Linux and C:\ for Windows.
        # e.g. /dev1 for Linux, C:\dev1 for Windows.
        # May take a while...
        for current_path, dirs, files in os.walk(os_root_and_base):
            for directory in config[CONFIGURATION]:
                if directory != "base_directory":
                    option_value = config.get(CONFIGURATION, directory)
                    if current_path.find(option_value) >= 0:
                        # Create a new section if necessary, based on the CONFIGURATION section's option.
                        if not config.has_section(option_value):
                            config.add_section(option_value)
                        # Add each file as the option's name and the file's path as the option's value.
                        for file in files:
                            if config.has_option(option_value, file):
                                # If there are multiple files with the same name, create a csv for the value.
                                ov = config.get(option_value, file)
                                nv = ov + ", " + os.path.join(current_path, file)
                                config.set(option_value, file, nv)
                            else:
                                config.set(option_value, file, os.path.join(current_path, file))
    with open(os.path.join(absolute_path, file_name), "w") as config_file:
        config.write(config_file)
        config_file.close()
        print("File list compiled.")


def get_config(absolute_path: str = root_directory, file_name: str = base_config_name) -> str:
    """
    Retrieves the configuration file path needed.

    :param absolute_path: The path to the configuration file.
    :param file_name: The name of the configuration file.
    :return: The configuration file path.
    """
    config_file = Path(str(os.path.join(absolute_path, file_name)))

    # Create a new configuration file if it does not exist.
    if not config_file.exists():
        config_file = __create_config(absolute_path)

    return config_file


def select_build(file_name: str) -> str:
    """
    Reads, display, then allow the selection of a specific build from the configuration file.

    :param file_name: The configuration file.
    :return: The selected build name, or None if no builds are available in the configuration file.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    sections = config.sections()
    sections.remove(CONFIGURATION)
    sections.remove(HOST_NAMES)
    index = None
    selection = None

    # Get user's selection.
    while True:
        if len(sections) <= 0:
            print("There are no builds saved in the configuration file!")
            break
        print("\nBuild list:")
        for section in sections:
            print("\t", str((sections.index(section) + 1)) + ").".ljust(5), section)
        while not index:
            try:
                index = int(input("Enter a build number: "))
                if index < len(sections) or index > len(sections):
                    index = None
                    print("Invalid selection!")
            except ValueError:
                # User entered a non-integer value, looping back.
                pass
        selection = sections[index - 1]
        print("\nBuild [%s] selected:" % selection)
        __print_options(config, selection)
        confirm = input("Enter 'y/Y' to confirm selection: ")
        if confirm in ["y", "Y"]:
            break
        else:
            index = None
    return selection


def build_paths(file_name: str, section: str) -> List[Tuple[str, str]]:
    """
    Build all the file paths for section based on the section's options.

    :param file_name: The configuration file to use.
    :param section: The build name to use.
    :return: A list containing tuples of section name and absolute paths pairings of all files described in the
             section's option.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    subsection = config[section]
    retrieved_files = []
    skipped_hosts = {}

    file_list = configparser.ConfigParser()
    file_list.read(config.get(CONFIGURATION, "file_list"))
    file_list_sections = file_list.sections()

    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in subsection:
        # The files are in a csv format while the guide will be a whole directory containing multiple documents.
        build_list = list(map(lambda x: x.strip(), config.get(section, entry).split(",")))
        for file in build_list:
            for directory in file_list_sections:
                if file_list.has_option(directory, file):
                    for x in file_list.get(directory, file).split(","):
                        retrieved_files.append((directory, x.strip()))

    available_files = list(map(lambda x: os.path.split(x[1])[1], retrieved_files))
    for entry in subsection:
        build_list = list(map(lambda x: x.strip(), config.get(section, entry).split(",")))
        for file in build_list:
            if file not in available_files:
                skipped_hosts[entry] = config[section][entry]
    if skipped_hosts:
        print("\n*WARNING* Path does not exist in \"CONFIGURATION\" for the following host(s), and has been skipped:")
        for entry in skipped_hosts:
            text = entry
            if len(text) > 20:
                text = entry[:17] + "..."
            print("\t", text.ljust(20), "=", skipped_hosts[entry])
        input("Press [Enter] key to acknowledge...")

    return retrieved_files


def __print_options(config: configparser.ConfigParser, section: str):
    """
    Helper method to display all of the options in a section.

    :param config: The configuration file to use.
    :param section: The build name to use.
    """
    options = config[section]
    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in options:
        text = entry
        if len(text) > 20:
            text = entry[:17] + "..."
        print("\t", text.ljust(20), "=", config.get(section, entry))


def add_new_build(file_name: str):
    """
    Add a new build configuration.

    :param file_name: The configuration file to save into.
    """
    config = configparser.ConfigParser()
    config.read(file_name)

    while True:
        build_title = input("Please enter a build name: ")
        if not config.has_section(build_title):
            break
        print("The build name already exist!")
    build_options = __create_dict(file_name)
    print("Saving [%s] into the config file..." % build_title)
    with open(os.path.join(file_name), "a") as config_file:
        config = configparser.ConfigParser()
        config.add_section(build_title)
        config[build_title] = build_options
        config.write(config_file)
        config_file.close()
        print("New build configuration saved.")


def __create_dict(file_name: str) -> Dict[str, str]:
    """
    Create a dictionary from user's input.

    :param file_name: The configuration file to get the CONFIGURATION section for keys.
    :return: A dictionary based on CONFIGURATION section and user's input.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    default = config[HOST_NAMES]
    new_build = {}
    confirm = False
    print("\n*Enter either a comma separated value of multiple files or a single file*")

    while not confirm:
        for key in default:
            if default.get(key) == "True":
                entry = ""
                while not entry:
                    entry = input("Please enter value for option [%s]: " % key)
                    entry.strip()
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


def remove_build(file_name: str):
    """
    Remove a section (build) from the configuration file.

    :param file_name: The configuration file to use.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    build = select_build(file_name)
    confirm = input("Removing [%s] from the configuration file, enter the build name exactly to confirm: " % build)
    if confirm.rstrip() == build:
        config.remove_section(build)
        with open(file_name, "w") as config_file:
            config.write(config_file)
            config_file.close()
            print("Build [%s] has been removed from the configuration." % build)
    else:
        print("Aborting operation.")


def edit_build(file_name: str):
    """
    Edits an existing section (build) in the configuration file.

    :param file_name: The configuration file to use.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    build = select_build(file_name)
    confirm = input("Editing build [%s], enter the build name exactly to confirm: " % build)
    if confirm.rstrip() == build:
        while True:
            options = config.options(build)
            print("Leave blank to use current value(s), otherwise enter new values...")
            new_value = __create_dict(file_name)
            for option in options:
                if option in new_value and new_value[option].strip():
                    config[build][option] = new_value.get(option)
            __print_options(config, build)
            selection = input("Enter 'y/Y' to confirm entries: ")
            if selection in ["y", "Y"]:
                with open(file_name, "w") as f:
                    config.write(f)
                    f.close()
                    print("Build [%s]'s options changed!" % build)
                break
    else:
        print("Aborting operation.")


def cherry_pick(file_name: str):
    # TODO: Allow user to pick a certain option from a section to copy.
    pass


def print_storage():
    # TODO: display the tree of the "image repo" and its content.
    pass


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
    except:
        o_binary = 0
    read_flags = os.O_RDONLY | o_binary
    write_flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | o_binary
    buffer_size = 128 * 1024
    try:
        file_in = os.open(src, read_flags)
        stat = os.fstat(file_in)
        file_out = os.open(dst, write_flags, stat.st_mode)
        with tqdm.tqdm(desc=os.path.split(src)[1], total=stat.st_size, unit_scale=True, unit='') as bar:
            for x in iter(lambda: os.read(file_in, buffer_size), b''):
                os.write(file_out, x)
                bar.update(len(x))
    except:
        # TODO: Catch an actual error type.
        print("Copy failed for %s!" % src)
    finally:
        try:
            os.close(file_in)
        except:
            # TODO: Catch an actual error type.
            pass
        try:
            os.close(file_out)
        except:
            # TODO: Catch an actual error type.
            pass


def create_test_storage_environment():
    print("Creating test environment...")
    # "firmware_directory": "firmware",
    # "network_directory": "network",
    # "images_directory": "volume",
    # "iso_directory": "ISO_images",
    # "config_directory": "configs",
    # "delta_directory:": "deltas",
    # "tools_directory": "tools"}
    test_directory = [os.path.join(os.path.abspath(os.sep), "file-picker-dev1", "firmware"),
    os.path.join(os.path.abspath(os.sep), "file-picker-dev1", "firmware", "network"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev1", "firmware", "volume"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev2", "firmware"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev2", "firmware", "ISO_images"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev3", "configs"),
                      os.path.join(os.path.abspath(os.sep), "file-picker-dev3", "tools")]
    test_files = ["test_1.1", "test_1.2", "test_1.3",
                  "test_2", "test_3", "test_4",
                  "install", "test", "misc",
                  "duplicate_file", "duplicate_file"]
    for x in test_directory:
        if not Path(x).exists():
            os.makedirs(x)
    for file in test_files:
        random_index = random.randrange(len(test_directory) - 1)
        with open(os.path.join(test_directory[random_index], file), 'wb') as f:
            f.write(os.urandom(16 * 1024 * 1024))  # 16 MB fake files.
            # f.write(os.urandom(128 * 1024)) # 128 KB fake files.
            f.close()


def main():
    # TESTING
    create_test_storage_environment()
    test_file = get_config()
    print("Test file:", test_file)
    while True:
        print("***TEST MENU***")
        print("\t1). Select a build.")
        print("\t2). Remove a build.")
        print("\t3). Add a build.")
        print("\t4). Edit a build.")
        print("\t5). Cherry-pick from build (Not implemented yet).")
        print("\t6). Add new files (Not implemented yet).")
        # Will try to associate files to build options and print
        # what's not being used as well as what files are missing for a build.
        print("\t7). Print report (Not implemented yet).")
        print("\t8). Print verbose tree structure (Not implemented yet).")
        print("\t9). Reset test environment.")
        print("\t0). Exit.")
        try:
            selection = input("Enter a number: ")
            if selection == "1":
                build = select_build(test_file)
                if build:
                    files = build_paths(test_file, build)
                    destination = str(os.path.join(home, "file-picker", "test-destination"))
                    if not Path(destination).exists():
                        os.makedirs(destination)
                    print("Copying the following files to %s:" % destination)
                    for file in files:
                        print("\t %s" % file[1])
                    copy_files(files, destination)
            elif selection == "2":
                remove_build(test_file)
            elif selection == "3":
                add_new_build(test_file)
            elif selection == "4":
                edit_build(test_file)
            elif selection == "9":
                shutil.rmtree(root_directory)
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev1"))
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev2"))
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev3"))
                create_test_storage_environment()
                test_file = get_config()
            elif selection == "0":
                break
            else:
                pass
        except ValueError:
            pass
    shutil.rmtree(root_directory)
    shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev1"))
    shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev2"))
    shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev3"))


if __name__ == "__main__":
    main()
