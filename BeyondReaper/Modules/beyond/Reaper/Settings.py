# Step 1 - RemoteControl.py Action and its Command ID
# =======================================================================

Reaper_RemoteControl_CommandID = "_RS56e75b07771d64aa2f514ad1390361fe5fe65943"

# From Reaper's "Actions/Show action list..." press "ReaScript: Load..."
# Find and select file "...\Modules\beyond\Reaper\RemoteControl.py"
# Back on the Actions list, you will see "Script: RemoteControl.py"
# Right click on it and select "Copy selected action command ID"
# Paste that into quotes above.




# Step 2 - Reaper's OSC and Addresses
# =======================================================================

Reaper_OSC_Address = ("localhost", 8000)
External_Program_Address = ("localhost", 8001)

# From Reaper's "Options/Preferences" select "Control Surfaces" page.
#
# If the "Control Surfaces" has an item beginning with "OSC:", you have 
# a preexisting OSC setup, see below.
#
# Press "Add" and select "OSC (Open Sound Control)".
#
# Make sure the "Pattern config:" is set to Default.
#
# Checkmark and Activate "Receive on port:"
#
# The default Port of 8000 and the "localhost" addresses above are fine
# for connecting to Reaper locally on the same computer only.  Reaper
# shows the local IP it is running on which is equivalent to "localhost".
# If you need to connect to Reaper across a network, change these addresses
# above to match Reaper and where the External Programs will be running.
# 
# 
# Preexisting OSC Setup:
# ======================
# 
# If your "Pattern config:" is not Default, make sure you have the following
# standard line in your Pattern config file:
# 
# ACTION i/action s/action/str t/action/@ f/action/@/cc
# 
# Or, you may setup another Default OSC configuration as above on 
# another Port and enter that Port above.




# Step 3 - Python Executable
# =======================================================================

Python = r"C:\Program Files\Python37\pythonw.exe"

# Enter the path of your preferred Python executable
#
# On Windows, example:
# Python = r"C:\Users\...\AppData\Local\Programs\Python\Python35-32\pythonw.exe"
# Keep the r" to preserve the \'s
#
# On OSX, example:
# Python = "/Library/Frameworks/Python.framework/Versions/3.4/Resources/Python.app/Contents/MacOS/Python"
#
# This will allow you to launch an External beyond.Reaper programs as
# Reaper Actions bound to keyboard shortcuts, menus and toolbars.