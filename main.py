import os
import configparser
import shutil
from pathlib import Path
from typing import Union, List

base_config = "config.ini"
home = str(os.path.expanduser("~"))
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
              "guide": "test_guide_directory"}


def create_config(absolute_path: str,
                  fname: str = base_config,
                  configuration: dict = None) -> str:
    """
    Creates a configuration file to be used.

    :param absolute_path: The location the file will be created.
    :param fname: The name of the configuration file.
    :param configuration: The configuration to be entered into the file.
    :return: The newly created configuration file's path.
    """
    print("Creating base config file.")

    if configuration is None:
        configuration = base_paths

    if not Path(absolute_path).exists():
        os.makedirs(absolute_path)
    config = configparser.ConfigParser()
    config["DEFAULT"] = configuration

    # TODO: Remove this line!
    config["test_build"] = test_build

    with open(os.path.join(absolute_path, fname), "w") as config_file:
        config.write(config_file)
        config_file.close()
        print("Base config file created.")

    return os.path.join(absolute_path, fname)


def get_config(fname: str = base_config) -> str:
    """
    Retrieves the configuration file path needed.

    :param fname: The name of the configuration file.
    :return: The configuration file path.
    """
    root_directory = str(os.path.join(home, "file-picker"))
    config_file = Path(str(os.path.join(root_directory, fname)))

    if not config_file.exists():
        config_file = create_config(root_directory)

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

    while not index:
        index = int(input("Enter a build number: "))
        if index < len(sections) or index > len(sections):
            index = None
            print("Invalid selection!")

    selection = sections[index - 1]
    print("\nBuild", selection, "selected:")
    subsection = config[selection]
    files = []

    for entry in subsection:
        print("\t", entry.ljust(20), "=", subsection[entry])
        if "guide" not in entry:
            images = config[selection][entry].split(",")
            for image in images:
                path = os.path.join(config["DEFAULT"][entry], image.strip())
                files.append(path)
        else:
            path = os.path.join(config["DEFAULT"][entry], config[selection][entry])
            files.append(path)

    return files


# TESTING
test_file = get_config()
print("Test file:", test_file)
confirm = False
while not confirm:
    files = select_build(test_file)
    selection = input("Enter 'y/Y' to confirm selection, otherwise 'n/N': ")
    if selection in ["y", "Y"]:
        confirm = True
for file in files:
    print(file)
shutil.rmtree(str(os.path.join(home, "file-picker")))










