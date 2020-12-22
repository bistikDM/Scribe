import collections
import configparser
import os
import shutil
from pathlib import Path
from typing import List, Union, OrderedDict

import build
import copy
import setup
import test_env


def select_build() -> str:
    """
    Reads, display, then allow the selection of a specific build from the configuration file.

    :return: The selected build name, or None if no builds are available in the configuration file.
    """
    index = None
    selection = None
    sections = build.get_builds()

    # Get user's selection.
    while True:
        if len(sections) <= 0:
            print("There are no builds saved in the configuration file!")
            break
        print("\nBuild list:")
        display_entries(sections, numbered=True)
        while not index:
            index = input("Enter a build number: ")
            if not is_value_valid_int(index, len(sections)):
                index = None
                print("Invalid selection!")
        selection = sections[int(index) - 1]
        print("\nBuild [%s] selected:" % selection)
        try:
            options = build.get_options(setup.get_config(), selection)
            display_entries(options)
        except build.EmptySectionError:
            print("Section [%s] has no options!" % selection)
        except configparser.NoSectionError:
            print("The section [%s] does not exist in [%s]!" % (selection, setup.get_config()))
        confirm = input("Enter 'y/Y' to confirm selection: ")
        if confirm in ["y", "Y"]:
            break
        else:
            index = None
    return selection


def print_storage():
    # TODO: display the tree of the "image repo" and its content.
    pass


def display_entries(entries: Union[List[str], OrderedDict[str, str]], numbered: bool = False):
    """
    Prints all of the entries passed in the argument.

    :param entries: The entries to display.
    :param numbered: True if the entries should be numbered, otherwise false.
    """
    if isinstance(entries, List):
        for entry in entries:
            if numbered:
                print("\t", (str((entries.index(entry) + 1)) + ").").ljust(5), entry)
            else:
                print("\t", entry)
    else:
        keys = list(entries.keys())
        for k, v in entries.items():
            text = k
            if len(text) > 20:
                text = k[:17] + "..."
            if numbered:
                print("\t", (str((keys.index(k) + 1)) + ").").ljust(5), text.ljust(20), "=", v)
            else:
                print("\t", text.ljust(20), "=", v)


def get_new_build_option() -> OrderedDict[str, str]:
    """
    Create an ordered dictionary from user's input.

    :return: An ordered dictionary based on CONFIGURATION section and user's input.
    """
    config_options = build.get_options(setup.get_config(), setup.CONFIGURATION_SECTION)
    file_list_path = config_options[setup.file_list_config_name]
    host_name_options = build.get_options(setup.get_config(), setup.HOST_NAMES_SECTION)
    new_build = collections.OrderedDict()
    confirm = False
    print("\n*Enter either a comma separated value of multiple files or a single file*")
    print("*e.g. 1 for a single file or 1, 3, 5 for multiple files.*")
    while not confirm:
        for k, v in host_name_options.items():
            if v.strip() == "True":
                try:
                    valid = False
                    current_options = build.get_options(file_list_path, k)
                    while not valid:
                        print("\n Selecting %s:" % k)
                        display_entries(current_options, numbered=True)
                        raw_entry = input("Please enter value for option [%s]: " % k)
                        if raw_entry.strip():
                            # Validating entries.
                            section_size = len(current_options)
                            processed_entries = list(filter(None, map(lambda x: x.strip(), raw_entry.split(","))))
                            checked_entries = list(
                                map(lambda x: is_value_valid_int(x, section_size), processed_entries))
                            if False in checked_entries:
                                print("Option [%s] contains an invalid entry!" % k)
                                valid = False
                            else:
                                valid = True
                        else:
                            # Assume blank entries are valid.
                            valid = True
                        new_build[k] = raw_entry
                except (configparser.NoSectionError, build.EmptySectionError) as e:
                    if isinstance(e, build.EmptySectionError):
                        print("Section [%s] has no options!" % k)
                    else:
                        print("The section [%s] does not exist in [%s]!" % (k, file_list_path))
                    print("Skipping [%s]..." % k)
        for entry in new_build:
            # Convert numerical entries into valid file names.
            value = new_build[entry].strip()
            if value:
                processed_values = list(filter(None, map(lambda x: x.strip(), value.split(","))))
                processed_values = list(map(int, processed_values))
                new_build[entry] = build.convert_to_filenames(file_list_path, processed_values, entry)
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


def is_value_valid_int(value: str, maximum: int) -> bool:
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


def main():
    # TESTING
    test_env.create_test_storage_environment()
    configuration_file = setup.get_config()
    print("Configuration file:", configuration_file)
    while True:
        print("***TEST MENU***")
        print("\t1). Select a build.")
        print("\t2). Remove a build.")
        print("\t3). Add a build.")
        print("\t4). Edit a build.")
        print("\t5). Cherry-pick from build.")
        print("\t6). Rebuild file-list.ini.")
        # Will try to associate files to build options and print
        # what's not being used as well as what files are missing for a build.
        print("\t7). Print report (Not implemented yet).")
        print("\t8). Print verbose tree structure (Not implemented yet).")
        print("\t9). Reset test environment.")
        print("\t0). Exit.")
        try:
            selection = input("Enter a number: ")
            if selection == "1":
                # Select a build.
                selected_build = select_build()
                if selected_build:
                    skipped_options, files = build.build_paths(selected_build)
                    if skipped_options:
                        print("\n*WARNING* File association does not exist in [%s] for the following" 
                              " option(s), and has been skipped:" % setup.file_list_config_name)
                        display_entries(skipped_options)
                        input("Press [Enter] key to acknowledge...")
                    destination = str(os.path.join(setup.project_root, "test-destination"))
                    if not Path(destination).exists():
                        os.makedirs(destination)
                    print("Copying the following files to %s:" % destination)
                    for file in files:
                        print("\t %s" % file[1])
                    copy.copy_files(files, destination)
            elif selection == "2":
                # Remove a build.
                selected_build = select_build()
                if selected_build:
                    confirm = input(
                        "Removing [%s] from the configuration file, enter the build name exactly to confirm: " %
                        selected_build)
                    if confirm.strip() == selected_build:
                        build.remove_build(selected_build)
                        print("Build [%s] has been removed from the configuration." % selected_build)
                    else:
                        print("Aborting operation.")
            elif selection == "3":
                # Add a build.
                sections = build.get_builds()
                while True:
                    build_title = input("Please enter a build name: ").strip()
                    if build_title not in sections:
                        break
                    print("The build name already exist!")
                build_options = get_new_build_option()
                print("Saving [%s] into the config file..." % build_title)
                build.add_new_build(build_title, build_options)
                print("New build configuration saved.")
            elif selection == "4":
                # Edit a build.
                selected_build = select_build()
                if selected_build:
                    confirm = input("Editing build [%s], enter the build name exactly to confirm: " % selected_build)
                    if confirm.strip() == selected_build:
                        print("Leave blank to use current value(s), otherwise enter new values...")
                        new_value = get_new_build_option()
                        build.edit_build(selected_build, new_value)
                        print("Build [%s]'s options changed!" % selected_build)
                else:
                    print("Aborting operation.")
            elif selection == "5":
                # Cherry pick a build.
                selected_build = select_build()
                if selected_build:
                    build_options = build.get_options(setup.get_config(), selected_build)
                    display_entries(build_options, numbered=True)
                    index = None
                    while not index:
                        index = input("Enter an option number: ")
                        if not is_value_valid_int(index, len(build_options)):
                            index = None
                            print("Invalid selection!")
                    selection = list(build_options.keys())[int(index) - 1]
                    print("\nOption [%s] selected:" % selection)
                    skipped_options, files = build.build_paths(selected_build)
                    if selection not in skipped_options:
                        filtered_files = list(filter(lambda x: x[0] == selection, files))
                        destination = str(os.path.join(setup.project_root, "test-destination"))
                        if not Path(destination).exists():
                            os.makedirs(destination)
                        print("Copying the following files to %s:" % destination)
                        for file in filtered_files:
                            print("\t %s" % file[1])
                        copy.copy_files(filtered_files, destination)
                    else:
                        print("Could not located the file associated with the selected option [%s]..." % selection)
            elif selection == "6":
                setup.update_file_list(setup.project_root, setup.file_list_config_name)
            elif selection == "9":
                shutil.rmtree(setup.project_root)
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev1"))
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev2"))
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev3"))
                test_env.create_test_storage_environment()
            elif selection == "0":
                break
            else:
                pass
        except ValueError:
            pass
    shutil.rmtree(setup.project_root)
    shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev1"))
    shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev2"))
    shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev3"))


if __name__ == "__main__":
    main()
