# file-picker (TBD)
This script provides a base functionality that automates the 
creation of deployable builds that can be used in conjunction with other tools.

The goal of this script is to eliminate the need for the user to 
manually select each individual VM image from their repository 
in order to create a deployable build. By using a configuration 
file, the user will be able to select a build version and the 
script will automatically copy all the specified VM images 
associated with that build version to a specified destination.

# Get started
1. `pip install -r requirements.txt` to install required dependecies.
2. `python main_cli.py -demo` to see how it works or `python main_cli.py` to start using it.
3. Optional: `pyinstaller -F main_cli.py` will create an executable that does not need an interpreter or 
   any modules to run. It will be inside the `dist` directory.
