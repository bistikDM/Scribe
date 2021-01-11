import collections
import configparser
import os
from pathlib import Path
from typing import Dict, OrderedDict

USER_HOME = str(os.path.expanduser("~"))
CONFIGURATION_SECTION = "CONFIGURATION"
HOST_NAMES_SECTION = "HOST_NAMES"
base_config_name = "config.ini"
file_list_config_name = "file-list.ini"
project_root = str(os.path.join(USER_HOME, "Scribe"))
base_paths = {file_list_config_name: str(os.path.join(project_root, file_list_config_name))}
demo = False

file_list_default = collections.OrderedDict({"base_directory": "Scribe-dev1, Scribe-dev2, Scribe-dev3",
                                             "firmware_directory": "firmware",
                                             "network_directory": "network",
                                             "images_directory": "volume",
                                             "iso_directory": "ISO_images",
                                             "config_directory": "configs",
                                             "delta_directory:": "deltas",
                                             "tools_directory": "tools"})

default_host_names = {"firmware": "True",
                      "network": "True",
                      "volume": "True",
                      "ISO_images": "True",
                      "configs": "True",
                      "deltas": "True",
                      "tools": "True"}

demo_build = {"firmware": "test_1.1, test_1.2, test_1.3",
              "network": "test_2",
              "volume": "test_3",
              "ISO_images": "test_4",
              "configs": "test_5",
              "deltas": "test_6",
              "tools": "install, test, misc"}


def demo_mode():
    """
    Configure the script to run in demo mode without interfering with existing .ini files.

    :return:
    """
    global base_config_name
    global file_list_config_name
    global project_root
    global demo
    global base_paths
    base_config_name = "config-demo.ini"
    file_list_config_name = "file-list-demo.ini"
    project_root = str(os.path.join(USER_HOME, "Scribe-demo"))
    base_paths = {file_list_config_name: str(os.path.join(project_root, file_list_config_name))}
    demo = True


def initialize():
    """
    Convenience method to initialize everything at startup.

    :return:
    """
    create_config()
    create_file_list_config()
    crawl_system()


def get_config(path: str = None, file_name: str = None) -> str:
    """
    Retrieves the configuration file path needed.

    :param path: The path to the configuration file.
    :param file_name: The name of the configuration file.
    :return: The configuration file path.
    """
    if path is None:
        path = project_root
    if file_name is None:
        file_name = base_config_name
    config_file = Path(str(os.path.join(path, file_name)))
    return config_file


def create_config(path: str = None, file_name: str = None, configuration: Dict = None,
                  host_names: Dict = None) -> str:
    """
    Creates a configuration file to be used.

    :param path: The location the file will be created.
    :param file_name: The name of the configuration file.
    :param configuration: The configuration to be entered into the file.
    :param host_names: The default host names to use.
    :return: The newly created configuration file's path.
    """
    if path is None:
        path = project_root
    if file_name is None:
        file_name = base_config_name
    # Use default dictionary if none is given.
    if configuration is None:
        configuration = base_paths
    if host_names is None:
        host_names = default_host_names

    # Create the directories if it does not exist.
    if not Path(path).exists():
        os.makedirs(path)
    config = configparser.ConfigParser()
    # Preserve case-sensitivity.
    config.optionxform = str
    config[CONFIGURATION_SECTION] = configuration
    config[HOST_NAMES_SECTION] = host_names

    if demo:
        config["demo_build"] = demo_build

    # Write the configuration into the file.
    with open(os.path.join(path, file_name), "w") as config_file:
        config.write(config_file)

    return os.path.join(path, file_name)


def create_file_list_config(path: str = None, file_name: str = None,
                            configuration: OrderedDict[str, str] = None):
    """
    Creates a configuration file to be used.

    :param path: The location the file will be created.
    :param file_name: The name of the configuration file.
    :param configuration: The configuration to be entered into the file.
    :return: The newly created configuration file's path.
    """
    if path is None:
        path = project_root
    if file_name is None:
        file_name = file_list_config_name
    if configuration is None:
        configuration = file_list_default

    if not Path(path).exists():
        os.makedirs(path)
    config = configparser.ConfigParser()
    # Preserve case-sensitivity.
    config.optionxform = str
    config[CONFIGURATION_SECTION] = configuration

    with open(os.path.join(path, file_name), "w") as config_file:
        config.write(config_file)


def crawl_system(path: str = None, file_name: str = None):
    """
    Crawls the system using the supplied configuration file as the starting point. It will populate the file with
    discovered files.

    :param path: The location of the configuration file.
    :param file_name: The name of the configuration file.
    """
    if path is None:
        path = project_root
    if file_name is None:
        file_name = file_list_config_name
    config = configparser.ConfigParser()
    # Preserve case-sensitivity.
    config.optionxform = str
    config.read(os.path.join(path, file_name))
    for section in config.sections():
        if section != CONFIGURATION_SECTION:
            config.remove_section(section)

    # Crawling block.
    # Iterate over a list created out of the base_directory option.
    for base in filter(None, map(lambda x: x.strip(), config.get(CONFIGURATION_SECTION, "base_directory").split(","))):
        # print("Crawling %s..." % base)
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
                            file_no_ext = os.path.splitext(file)[0]
                            if config.has_option(option_value, file_no_ext):
                                # If there are multiple files with the same name, create a csv for the value.
                                ov = config.get(option_value, file_no_ext)
                                nv = ov + ", " + os.path.join(current_path, file)
                                config.set(option_value, file_no_ext, nv)
                            else:
                                config.set(option_value, file_no_ext, os.path.join(current_path, file))
    with open(os.path.join(path, file_name), "w") as config_file:
        config.write(config_file)
