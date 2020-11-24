import configparser
import os
import shutil
import time
from pathlib import Path
from typing import Union, List, Dict

base_config = "config.ini"
home = str(os.path.expanduser("~"))
root_directory = str(os.path.join(home, "file-picker"))
base_paths = {"host_1": str(os.path.join(home, "file-picker", "host_1")),
              "host_2": str(os.path.join(home, "file-picker", "host_2")),
              "host_3": str(os.path.join(home, "file-picker", "host_3")),
              "host_4": str(os.path.join(home, "file-picker", "host_4")),
              "guide": str(os.path.join(home, "file-picker", "guide"))}

# TODO: Remove this variable!
test_build = {"host_1": "test_1.1, test_1.2, test_1.3",
              "host_2": "test_2",
              "host_3": "test_3",
              "host_4": "test_4",
              "host_5_does_not_exist": "does_not_exist",
              "guide": "test_guide_directory"}


def create_config(absolute_path: str,
                  file_name: str = base_config,
                  configuration: Dict = None) -> str:
    """
    Creates a configuration file to be used.

    :param absolute_path: The location the file will be created.
    :param file_name: The name of the configuration file.
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
    with open(os.path.join(absolute_path, file_name), "w") as config_file:
        config.write(config_file)
        config_file.close()
        print("Base config file created.")

    return os.path.join(absolute_path, file_name)


def get_config(absolute_path: str = root_directory, file_name: str = base_config) -> str:
    """
    Retrieves the configuration file path needed.

    :param absolute_path: The path to the configuration file.
    :param file_name: The name of the configuration file.
    :return: The configuration file path.
    """
    config_file = Path(str(os.path.join(absolute_path, file_name)))

    # Create a new configuration file if it does not exist.
    if not config_file.exists():
        config_file = create_config(absolute_path)

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


def build_paths(file_name: str, section: str) -> List[str]:
    """
    Build all the file paths for section based on the section's options.

    :param file_name: The configuration file to use.
    :param section: The build name to use.
    :return: A list containing the absolute paths of all files described in the section's option.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    subsection = config[section]
    files = []
    skipped_hosts = {}

    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in subsection:
        # The files are in a csv format while the guide will be a whole directory containing multiple documents.
        if "guide" not in entry:
            images = config[section][entry].split(",")
            for image in images:
                if config.has_option("DEFAULT", entry):
                    path = os.path.join(config["DEFAULT"][entry], image.strip())
                    files.append(path)
                else:
                    skipped_hosts[entry] = config[section][entry]
        else:
            if config.has_option("DEFAULT", entry):
                path = os.path.join(config["DEFAULT"][entry], config[section][entry])
                files.append(path)
            else:
                skipped_hosts[entry] = config[section][entry]

    if skipped_hosts:
        print("\n*WARNING* Path does not exist in \"DEFAULT\" for the following host(s), and has been skipped:")
        for entry in skipped_hosts:
            text = entry
            if len(text) > 20:
                text = entry[:17] + "..."
            print("\t", text.ljust(20), "=", skipped_hosts[entry])
        input("Press [Enter] key to acknowledge...")

    return files


def __print_options(config: configparser.ConfigParser, section: str):
    """
    Helper method to display all of the options in a section.

    :param config: The configuration file to use.
    :param section: The build name to use.
    """
    subsection = config[section]

    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in subsection:
        text = entry
        if len(text) > 20:
            text = entry[:17] + "..."
        print("\t", text.ljust(20), "=", subsection[entry])


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

    :param file_name: The configuration file to get the "DEFAULT" section for keys.
    :return: A dictionary based on "DEFAULT" section and user's input.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
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
    # TODO
    pass


def cherry_pick(file_name: str):
    # TODO: Allow user to pick a certain option from a section to copy.
    pass


def print_storage():
    # TODO: display the tree of the "image repo" and its content.
    pass


def copy_files(file_name: Union[str, List[str]], destination_directory: str):
    """
    Copies file(s) to the provided destination.

    :param file_name: The file(s) to be copied.
    :param destination_directory: The location where the file(s) will be copied to.
    :return: True if the operation was successful, otherwise false.
    """
    # Create the directories if it does not exist.
    if not Path(destination_directory).exists():
        os.makedirs(destination_directory)

    if isinstance(file_name, List):
        for file in file_name:
            head_tail = os.path.split(file)
            destination = os.path.join(destination_directory, head_tail[1])
            __copy(file, destination)
    else:
        head_tail = os.path.split(file_name)
        destination = os.path.join(destination_directory, head_tail[1])
        __copy(file_name, destination)


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
        start_time = time.process_time()
        file_in = os.open(src, read_flags)
        stat = os.fstat(file_in)
        file_out = os.open(dst, write_flags, stat.st_mode)
        for x in iter(lambda: os.read(file_in, buffer_size), b''):
            os.write(file_out, x)
        end_time = time.process_time()
        print("[%s] completed in: %s seconds." % (os.path.split(src)[1], round(end_time - start_time, 3)))
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


def main():
    # TESTING
    test_file = get_config()
    print("Test file:", test_file)
    while True:
        print("***TEST MENU***")
        print("\t1). Select a build.")
        print("\t2). Remove a build.")
        print("\t3). Add a build.")
        print("\t4). Edit a build (Not implemented yet).")
        print("\t0). Exit.")
        try:
            selection = int(input("Enter a number: "))
            if selection == 1:
                build = select_build(test_file)
                if build:
                    files = build_paths(test_file, build)
                    destination = str(os.path.join(home, "file-picker", "test-destination"))
                    if not Path(destination).exists():
                        os.makedirs(destination)
                    print("Creating fake files...")
                    for file in files:
                        if not Path(os.path.split(file)[0]).exists():
                            os.makedirs(os.path.split(file)[0])
                        with open(file, 'wb') as f:
                            f.write(os.urandom(16 * 1024 * 1024)) # 16 MB fake files.
                            # f.write(os.urandom(128 * 1024)) # 128 KB fake files.
                            f.close()
                    print("Copying the following files to %s:" % destination)
                    for file in files:
                        print("\t %s" % file)
                    start_time = time.process_time()
                    copy_files(files, destination)
                    stop_time = time.process_time()
                    print("Total time: %s seconds." % round(stop_time - start_time, 3))
            elif selection == 2:
                remove_build(test_file)
            elif selection == 3:
                add_new_build(test_file)
            elif selection == 4:
                edit_build(test_file)
            elif selection == 0:
                break
            else:
                pass
        except ValueError:
            pass
    shutil.rmtree(root_directory)


if __name__ == "__main__":
    main()
