import configparser
import os
import shutil
from pathlib import Path
from typing import List, Union, OrderedDict

import build_cli
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
    sections = build_cli.get_builds()

    # Get user's selection.
    while True:
        if len(sections) <= 0:
            print("There are no builds saved in the configuration file!")
            break
        print("\nBuild list:")
        display_entries(sections, numbered=True)
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
        try:
            options = build_cli.get_options(setup.get_config(), selection)
            display_entries(options)
        except build_cli.EmptySectionError:
            print("Section [%s] has no options!" % selection)
        except configparser.NoSectionError:
            print("The section [%s] does not exist in [%s]!" % (selection, setup.get_config()))
        confirm = input("Enter 'y/Y' to confirm selection: ")
        if confirm in ["y", "Y"]:
            break
        else:
            index = None
    return selection


def add_new_build():
    """
    Add a new build configuration.
    """
    sections = build_cli.get_builds()

    while True:
        build_title = input("Please enter a build name: ").strip()
        if build_title not in sections:
            break
        print("The build name already exist!")
    build_options = __create_dict(file_name)
    print("Saving [%s] into the config file..." % build_title)
    build_cli.add_new_build(build_title, build_options)
    print("New build configuration saved.")


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
        print("\t5). Cherry-pick from build (Not implemented yet).")
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
                selected_build = select_build()
                if selected_build:
                    skipped_options, files = build_cli.build_paths(selected_build)
                    if skipped_options:
                        print("\n*WARNING* File association does not exist in [%s] for the following" +
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
                build_cli.remove_build(configuration_file)
            elif selection == "3":
                build_cli.add_new_build(configuration_file)
            elif selection == "4":
                build_cli.edit_build(configuration_file)
            elif selection == "5":
                build_cli.cherry_pick(configuration_file)
            elif selection == "6":
                setup.update_file_list(setup.project_root, setup.file_list_config_name)
            elif selection == "9":
                shutil.rmtree(setup.project_root)
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev1"))
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev2"))
                shutil.rmtree(os.path.join(os.path.abspath(os.sep), "file-picker-dev3"))
                test_env.create_test_storage_environment()
                configuration_file = setup.get_config()
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
