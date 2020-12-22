import collections
import configparser
import os
from typing import List, Tuple, OrderedDict

import initialization


def get_builds() -> List[str]:
    """
    Retrieves all the sections available inside config.ini.

    :return: Returns a list containing all available sections inside config.ini excluding the
             "CONFIGURATION" and "HOST_NAMES" section.
    """
    config = configparser.ConfigParser()
    config.read(initialization.get_config())
    sections = config.sections()
    sections.remove(initialization.CONFIGURATION_SECTION)
    sections.remove(initialization.HOST_NAMES_SECTION)
    return sections


def get_options(config_file: str, section: str) -> OrderedDict[str, str]:
    """
    Retrieves all the options in a section of a configuration file.

    :param config_file: The full path to the configuration file to use.
    :param section: The section name to use.
    :return: An ordered {option: option value}, may raise a configparser.NoSectionError or EmptySectionError.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    try:
        options = config.options(section)
        option_dictionary = collections.OrderedDict()
        if options:
            for entry in options:
                option_dictionary[entry] = config.get(section, entry)
            return option_dictionary
        else:
            raise EmptySectionError
    except configparser.NoSectionError:
        raise


def build_paths(section: str) -> Tuple[OrderedDict[str, str], List[Tuple[str, str]]]:
    """
    Build all the file paths for section based on the section's options.

    :param section: The build name to use.
    :return: An ordered {option: filename} of skipped files and a list containing tuples of section name
             and absolute paths pairings of all files described in the section's option.
    """
    config = configparser.ConfigParser()
    config.read(initialization.get_config())
    subsection = config[section]
    retrieved_files = []
    skipped_options = collections.OrderedDict()
    file_list = configparser.ConfigParser()
    file_list.read(config.get(initialization.CONFIGURATION_SECTION, initialization.file_list_config_name))

    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in subsection:
        # The files are in a csv format while the guide will be a whole directory containing multiple documents.
        build_list = list(map(lambda i: i.strip(), config.get(section, entry).split(",")))
        for file in build_list:
            if file_list.has_option(entry, file):
                for i in file_list.get(entry, file).split(","):
                    retrieved_files.append((entry, i.strip()))
    available_files = list(map(lambda i: os.path.split(i[1])[1], retrieved_files))
    for entry in subsection:
        build_list = list(map(lambda i: i.strip(), config.get(section, entry).split(",")))
        for file in build_list:
            if file not in available_files:
                if entry in skipped_options.keys():
                    skipped_options[entry] = str(skipped_options.get(entry)) + ", " + file
                else:
                    skipped_options[entry] = file
    return skipped_options, retrieved_files


def add_new_build(section: str, options: OrderedDict[str, str]):
    """
    Add a new build configuration.

    :param section: The new build's name.
    :param options: The options for the new build.
    """
    config = configparser.ConfigParser()
    config.read(initialization.get_config())
    with open(os.path.join(initialization.get_config()), "a") as config_file:
        config = configparser.ConfigParser()
        config.add_section(section)
        config[section] = options
        config.write(config_file)


def remove_build(build: str):
    """
    Remove a section (build) from the configuration file.

    :param build: The build to remove from the configuration file.
    """
    config = configparser.ConfigParser()
    config.read(initialization.get_config())
    config.remove_section(build)
    with open(initialization.get_config(), "w") as config_file:
        config.write(config_file)
        config_file.close()


def edit_build(build: str, new_options: OrderedDict[str, str]):
    """
    Edits an existing section (build) in the configuration file.

    :param build: The build to edit.
    :param new_options: The new options for the edited build, if the value is blank then it will reuse the
                        old option's value.
    """
    config = configparser.ConfigParser()
    config.read(initialization.get_config())
    old_options = get_options(initialization.get_config(), build)
    for k, v in old_options.items():
        if k in new_options and new_options.get(k).strip():
            config[build][k] = new_options.get(k)
    with open(initialization.get_config(), "w") as f:
        config.write(f)


def convert_to_filenames(config_file: str, entries: List[int], section: str) -> str:
    """
    Helper method to convert numerical values to valid file names found in the configuration file.

    :param config_file: The full path to the configuration file to use.
    :param entries: A list of numerical values.
    :param section: The section to use from the configuration file.
    :return: A comma delimited string containing filename(s) retrieved from the configuration file.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    options = config.options(section)
    files = ""
    for entry in entries:
        files += options[entry - 1] + ", "
    return files.rstrip(", ")


class EmptySectionError(Exception):
    """
    The selected section is empty.
    """
    pass
