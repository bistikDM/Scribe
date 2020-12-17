import configparser
import os
from pathlib import Path
from typing import Dict

OS_HOME = str(os.path.expanduser("~"))
CONFIGURATION_SECTION = "CONFIGURATION"
HOST_NAMES_SECTION = "HOST_NAMES"
base_config_name = "config.ini"
file_list_config_name = "file-list.ini"
project_root = str(os.path.join(OS_HOME, "file-picker"))
base_paths = {"file_list": str(os.path.join(project_root, file_list_config_name))}

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


def get_config(absolute_path: str = project_root, file_name: str = base_config_name) -> str:
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


def update_file_list(absolute_path: str = project_root, file_name: str = file_list_config_name):
    """
    Updates the configuration file that contains a listing of all available files within the system.

    :param absolute_path: The location the file will be created.
    :param file_name: The name of the configuration file.
    """
    print("Updating file list...")
    __create_file_list_config(absolute_path, file_name)


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
    config[CONFIGURATION_SECTION] = configuration
    config[HOST_NAMES_SECTION] = host_names

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
    config[CONFIGURATION_SECTION] = file_list_default
    print("Discovering files, this may take a while...")

    # Crawling block.
    # Iterate over a list created out of the base_directory option.
    for base in map(lambda x: x.strip(), config.get(CONFIGURATION_SECTION, "base_directory").split(",")):
        os_root_and_base = os.path.join(os.path.abspath(os.sep), base)
        # Start crawling from the root directory + base, / for Linux and C:\ for Windows.
        # e.g. /dev1 for Linux, C:\dev1 for Windows.
        # May take a while...
        for current_path, dirs, files in os.walk(os_root_and_base):
            for directory in config[CONFIGURATION_SECTION]:
                if directory != "base_directory":
                    option_value = config.get(CONFIGURATION_SECTION, directory)
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
