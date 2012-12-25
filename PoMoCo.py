import os
import time
import re
import sys 
sys.dont_write_bytecode = True # keep the folders clean for beginners
sys.path.append('Moves') # include the moves folder
sys.path.append('PoMoCo')

import servotorComm
from robot import hexapod
import GUI

if __name__ == '__main__':

    controller = servotorComm.Controller() # Servo controller

    hexy = hexapod(controller)
    __builtins__.hexy = hexy # sets 'hexy' to be a gobal variable common to all modules
    __builtins__.floor = 60  # this is the minimum level the legs will reach

    # go through the Moves folder to find move files
    moves = []
    for fileName in os.listdir('Moves'):
        if os.path.splitext(fileName)[1] == '.py':
            fileName = os.path.splitext(fileName)[0]
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', fileName)
            moves.append(s1)
            __builtins__.moves = moves

    # global function for running move files
    def move(moveName):
        print "Preforming move:",moveName
        moveName = moveName.replace(' ','')
        if moveName in sys.modules:
            reload(sys.modules[moveName])
        else:
            __import__(moveName)
    __builtins__.move = move

    GUI.startGUI(controller)
    # the program only reaches here if the GUI has been closed
    del hexy
    del controller    
    print "quitting!"
    os._exit(0)