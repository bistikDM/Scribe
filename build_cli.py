import configparser
import os
from typing import List, Dict, Tuple

import setup


def select_build(file_name: str) -> str:
    """
    Reads, display, then allow the selection of a specific build from the configuration file.

    :param file_name: The configuration file.
    :return: The selected build name, or None if no builds are available in the configuration file.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    sections = config.sections()
    sections.remove(setup.CONFIGURATION_SECTION)
    sections.remove(setup.HOST_NAMES_SECTION)
    index = None
    selection = None

    # Get user's selection.
    while True:
        if len(sections) <= 0:
            print("There are no builds saved in the configuration file!")
            break
        print("\nBuild list:")
        for section in sections:
            print("\t", (str((sections.index(section) + 1)) + ").").ljust(5), section)
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
    file_list.read(config.get(setup.CONFIGURATION_SECTION, "file_list"))
    file_list_sections = file_list.sections()

    # Iterate through the entries and create a list that contains the absolute paths to all associated files.
    for entry in subsection:
        # The files are in a csv format while the guide will be a whole directory containing multiple documents.
        build_list = list(map(lambda i: i.strip(), config.get(section, entry).split(",")))
        for file in build_list:
            for directory in file_list_sections:
                if file_list.has_option(directory, file):
                    for i in file_list.get(directory, file).split(","):
                        retrieved_files.append((directory, i.strip()))

    available_files = list(map(lambda i: os.path.split(i[1])[1], retrieved_files))
    for entry in subsection:
        build_list = list(map(lambda i: i.strip(), config.get(section, entry).split(",")))
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


def remove_build(file_name: str):
    """
    Remove a section (build) from the configuration file.

    :param file_name: The configuration file to use.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    build = select_build(file_name)
    confirm = input("Removing [%s] from the configuration file, enter the build name exactly to confirm: " % build)
    if confirm.strip() == build:
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
    if confirm.strip() == build:
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


def __create_dict(file_name: str) -> Dict[str, str]:
    """
    Create a dictionary from user's input.

    :param file_name: The configuration file to get the CONFIGURATION section for keys.
    :return: A dictionary based on CONFIGURATION section and user's input.
    """
    config = configparser.ConfigParser()
    config.read(file_name)
    default = config[setup.HOST_NAMES_SECTION]
    file_list_config = configparser.ConfigParser()
    file_list_config.read(os.path.join(setup.project_root, setup.file_list_config_name))
    new_build = {}
    confirm = False
    print("\n*Enter either a comma separated value of multiple files or a single file*")
    print("*e.g. 1 for a single file or 1, 3, 5 for multiple files.*")

    while not confirm:
        for key in default:
            if default.get(key) == "True":
                try:
                    valid = False
                    while not valid:
                        print("\n Selecting %s:" % key)
                        __print_options(file_list_config, key, numbered=True)
                        raw_entry = input("Please enter value for option [%s]: " % key)
                        if raw_entry.strip():
                            # Validating entries.
                            section_size = len(file_list_config.options(key))
                            processed_entries = list(filter(None, map(lambda x: x.strip(), raw_entry.split(","))))
                            checked_entries = list(
                                map(lambda x: __is_value_valid_int(x, section_size), processed_entries))
                            if False in checked_entries:
                                print("Option [%s] contains an invalid entry!" % key)
                                valid = False
                            else:
                                valid = True
                        else:
                            # Assume blank entries are valid.
                            valid = True
                        new_build[key] = raw_entry
                except (configparser.NoSectionError, EmptySectionError) as e:
                    print("Skipping [%s]..." % key)
        for entry in new_build:
            # Convert numerical entries into valid file names.
            value = new_build[entry].strip()
            if value:
                processed_values = list(map(lambda x: int(x.strip()), value.split(",")))
                new_build[entry] = __convert_to_filenames(file_list_config, processed_values, entry)
        print("\nPlease confirm the selected options: ")
        for entry in new_build:
            text = entry
            if len(text) > 20:
                text = entry[:17] + "..."
            print("\t", text.ljust(20), "=", new_build[entry])
        selection = input("Enter 'y/Y' to confirm entries: ")
        if selection in ["y", "Y"]:
            confirm = True
    return new_build


def __convert_to_filenames(config: configparser.ConfigParser, entries: List[int], section: str) -> str:
    """
    Helper method to convert numerical values to valid file names found in the configuration file.

    :param config: The configuration file to use.
    :param entries: A list of numerical values.
    :param section: The section to use from the configuration file.
    :return: A comma delimited string containing filename(s) retrieved from the configuration file.
    """
    options = config.options(section)
    files = ""
    for entry in entries:
        files += options[entry - 1] + ", "
    return files.rstrip(", ")


def __print_options(config: configparser.ConfigParser, section: str, numbered: bool = False):
    """
    Helper method to display all of the options in a section.

    :param config: The configuration file to use.
    :param section: The build name to use.
    :param numbered: True if the list should be numbered, otherwise false.
    """
    try:
        options = config.options(section)
        # Iterate through the entries and create a list that contains the absolute paths to all associated files.
        if options:
            for entry in options:
                text = entry
                if len(text) > 20:
                    text = entry[:17] + "..."
                if numbered:
                    print("\t", (str((options.index(entry) + 1)) + ").").ljust(5), text.ljust(20), "=",
                          config.get(section, entry))
                else:
                    print("\t", text.ljust(20), "=", config.get(section, entry))
        else:
            print("Section [%s] has no options!" % section)
            raise EmptySectionError
    except configparser.NoSectionError:
        # The section does not exist in the file-list.ini, rethrowing!
        print("The section [%s] does not exist in file-list.ini!" % section)
        raise


def __is_value_valid_int(value: str, maximum: int) -> bool:
    """
    Helper method to determine if an input is a valid int value within the range of (0, maximum].

    :param value: The value to check.
    :param maximum: The inclusive maximum int value to check.
    :return: True if it is an int and within the specified values, otherwise False if it is not within the specified
             value or it is not an int.
    """
    try:
        if int(value):
            if 0 < int(value) <= maximum:
                return True
            else:
                return False
        else:
            return False
    except ValueError:
        # Definitely not an int.
        return False


class EmptySectionError(Exception):
    """
    The selected section is empty.
    """
    pass
