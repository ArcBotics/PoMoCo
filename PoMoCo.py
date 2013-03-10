import os
import time
import re
import sys 

# Keep the folders clean for beginners
sys.dont_write_bytecode = True

# Include the moves folder
sys.path.append('Moves')
sys.path.append('PoMoCo')

import servotorComm
from robot import hexapod
import GUI

if __name__ == '__main__':
    
    # Intialize the servo controller
    controller = servotorComm.Controller()
    
    # Set up the servo controller to run Hexy
    hexy = hexapod(controller)
    __builtins__.hexy = hexy # sets 'hexy' to be a global variable common to all modules
    __builtins__.floor = 60  # this is the minimum level the legs will reach
    
    # Go through the Moves folder to find move files
    moves = []
    for fileName in os.listdir('Moves'):
        if os.path.splitext(fileName)[1] == '.py':
            fileName = os.path.splitext(fileName)[0]
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', fileName)
            moves.append(s1)
            __builtins__.moves = moves
    
    # Function for running move files
    def move(moveName):
        print "Performing move:",moveName
        moveName = moveName.replace(' ','')
        if moveName in sys.modules:
            reload(sys.modules[moveName])
        else:
            __import__(moveName)
    
    # Make move global.
    __builtins__.move = move
    
    # Start the GUI. This will handle all further events.
    GUI.startGUI(controller)
    
    # The program only reaches this point if the GUI has been closed.
    # In this case, we want to clean up and exit.
    del hexy
    del controller
    print "Quitting!"
    os._exit(0)
