# file-picker
This script provides a base functionality that automates the 
creation of deployable builds that can be used in conjunction with other tools.

The goal of this script is to eliminate the need for the user to 
manually select each individual VM image from their repository 
in order to create a deployable build. By using a configuration 
file, the user will be able to select a build version and the 
script will automatically copy all the specified VM images 
associated with that build version to a specified destination.