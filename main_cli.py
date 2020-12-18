import os
import shutil
from pathlib import Path

import build_cli
import copy
import setup
import test_env


def print_storage():
    # TODO: display the tree of the "image repo" and its content.
    pass


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
                selected_build = build_cli.select_build(configuration_file)
                if selected_build:
                    files = build_cli.build_paths(configuration_file, selected_build)
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
