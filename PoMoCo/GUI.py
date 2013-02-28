from Tkinter import *
from tkFileDialog   import askopenfile
from tkFileDialog   import askopenfilename
from tkFileDialog   import asksaveasfile
from tkFileDialog   import asksaveasfilename

import os
import ConfigParser
from servotorComm import runMovement

FPS = 10

class App:
    
    def __init__(self, master, controller):
        self.con = controller
        self.master = master

        self.frame = Frame(self.master)

        self.frame.pack()

        # Setup menu system
        menu = Menu(root)
        root.config(menu=menu)
        filemenu = Menu(menu)

        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New")
        filemenu.add_command(label="Save Offsets", command=self.saveOffsets)
        
        # TODO: Bring these over from servitorGui
        #filemenu.add_command(label="Open Offsets", command=self.openOffsets)
        #filemenu.add_command(label="Save Positions", command=self.savePositions)
        #filemenu.add_command(label="Open Positions", command=self.openPositions)

        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quitApp)
        master.createcommand('exit', self.quitApp)  

        # Setup kill button
        self.killButton = Button(self.frame, text="Kill All Servos",fg="red",
                                font=("Helvetica", 20),command=self.estop)
        self.killButton.grid(row=0,column=14)

        self.loadOffsets()

        self.servos = []
        # Setup left side, 4 groups of 4 servo controls
        for i in xrange(4):
            self.newServo(0+i*4,[1,8+i*5])
            self.newServo(1+i*4,[1,9+i*5])
            self.newServo(2+i*4,[1,10+i*5])
            self.newServo(3+i*4,[1,11+i*5])
            self.addSpace([0,12+i*5])

        # Setup right side, 4 groups of 4 servo controls
        for i in xrange(4):
            self.newServo(16+i*4,[11,8+i*5])
            self.newServo(17+i*4,[11,9+i*5])
            self.newServo(18+i*4,[11,10+i*5])
            self.newServo(19+i*4,[11,11+i*5])
            self.addSpace([11,12+i*5])

        # Add some spaces for aesthetics
        self.addSpace([10,1])

        # Generate buttons for all move functions
        counter = 0
        for move_name in moves:
            b = Button(self.frame, text=move_name)
            b.move_name = move_name
            b.sel = lambda b = b: runMovement(move,b.move_name)
            b.config(command = b.sel)
            b.grid(row=counter+8, column=0)
            #b.pack()
            counter += 1

        self.poll()
        self.estop()

    def saveOffsets(self):
        cfgFile = asksaveasfile(filetypes = [('CFG', '*.cfg'),("All Files",".*")], defaultextension=".cfg")
        config = ConfigParser.ConfigParser()
        config.add_section("offsets")
        for servo in self.servos:
            offset = int(servo.offset.get().strip("+"))
            config.set("offsets", "%.3d"%(servo.servoNum), offset)
        config.write(cfgFile)

    def quitApp(self):
        root.quit()

    def poll(self):
        # Constantly updates the GUI based on the current status of the controller

        for servo in self.con.servos:
            pos = self.con.servos[servo].getPosuS()
            self.servos[servo].servoPos.set(pos)

            offset = self.con.servos[servo].getOffsetuS()
            self.servos[servo].offset.set(offset)

            active = self.con.servos[servo].getActive()
            if active:
                self.servos[servo].active.set(1)
            else:
                self.servos[servo].active.set(0)

        self.master.after(1000/FPS, self.poll)

    def addSpace(self,coords):
        l2 = Label(self.frame, text="\t\t", fg="red")
        l2.pack()
        l2.grid(row=coords[1], column=coords[0])

    def newServo(self,servoNum,coords):
        self.servos.append(servoGroup(self.frame,self.con,servoNum,colX=coords[0],rowY=coords[1]))

    def loadOffsets(self):
        # If there is one offset file in the folder, automatically load it
        off_files = []
        for filename in os.listdir(os.getcwd()):
            start, ext = os.path.splitext(filename)
            if ext == '.cfg':
                off_files.append(filename)

        if len(off_files) == 1:
            print "Opening",off_files[0]
            config = ConfigParser.ConfigParser()
            config.read(off_files[0])

            try:
                offsets = config.items('offsets')
                for offset in offsets:
                    servoNum = int(offset[0])
                    offset = int(offset[1])
                    for servo in self.con.servos:
                        if self.con.servos[servo].servoNum == servoNum:
                            #print "set servo",servoNum,"offset as",offset
                            self.con.servos[servo].setOffset(timing=offset)
                            break
                print "Automatically loaded offsets from",off_files[0]
            except:
                print "Automatic offset load failed, is there an offset file in the program directory?"

    def estop(self):
        self.con.killAll()
        
class servoGroup:
    def __init__(self,frame,con,servoNum,servoPos=1500,rowY=0,colX=0):
        self.frame = frame
        self.con = con
        self.frame.pack()

        self.v = IntVar()
        self.v.set(int(servoPos))
        self.active = IntVar()
        self.active.set(0)
        self.servoPos = IntVar()
        self.servoPos.set(servoPos)
        self.servoNum = servoNum

        offset = self.con.servos[self.servoNum].getOffsetuS()
        self.offset = StringVar()
        self.offset.set(int(offset))

        self.servoLabel = Label(self.frame, text="Servo %.2d"%(servoNum))
        self.servoLabel.grid(row=rowY, column=0+colX)

        self.onCheck = Checkbutton(self.frame, text="On", var=self.active,command=self.checkServo)
        self.onCheck.grid(row=rowY, column=1+colX)

        self.resetButton = Button(self.frame, text="Reset",command=self.resetServo)
        self.resetButton.grid(row=rowY, column=2+colX)


        self.posScale = Scale(self.frame, from_=500, to=2500, length=200, resolution=10,
                                orient=HORIZONTAL,showvalue=0,var=self.servoPos,command=self.moveServo)
        self.posScale.grid(row=rowY, column=3+colX)


        self.servoPosLabel = Label(self.frame,textvariable=self.servoPos)
        self.servoPosLabel.grid(row=rowY, column=4+colX)

        #offset label
        self.servoOffsetLabel = Label(self.frame,textvariable=self.offset)
        self.servoOffsetLabel.grid(row=rowY, column=5+colX)

        #offset plus
        self.offsetIncButton = Button(self.frame, text="+",command=self.offsetInc)
        self.offsetIncButton.grid(row=rowY, column=6+colX)

        #offset minus
        self.offsetDecButton = Button(self.frame, text="-",command=self.offsetDec)
        self.offsetDecButton.grid(row=rowY, column=7+colX)

    def checkServo(self):
        if self.active.get() == 0:
            self.active.set(0)
            self.con.servos[self.servoNum].kill()
            #print "Servo",self.servoNum,"activated"
        else:
            self.active.set(1)
            pos = self.servoPos.get()
            self.con.servos[self.servoNum].setPos(timing = pos)

            #print "Servo",self.servoNum,"killed"

    def moveServo(self,newServoPos):
        if self.active.get():
            self.con.servos[self.servoNum].setPos(int(newServoPos))
            self.con.servos[self.servoNum].move()
            self.servoPos.set(int(newServoPos))
            self.v.set(int(newServoPos))
        #print "set servo",self.servoNum,"to",newServoPos

    def resetServo(self):
        #print "reset servo",self.servoNum
        self.con.servos[self.servoNum].reset()

    def offsetInc(self):
        offset = self.con.servos[self.servoNum].getOffsetuS()
        self.con.servos[self.servoNum].setOffset(timing=offset+10)
        self.offset.set(offset+10)
        #print "servo",self.servoNum,"offset increased to",self.offset

        self.con.servos[self.servoNum].move()

    def offsetDec(self):
        offset = self.con.servos[self.servoNum].getOffsetuS()
        self.con.servos[self.servoNum].setOffset(timing=offset-10)
        self.offset.set(offset-10)
        #print "servo",self.servoNum,"offset increased to",self.offset
        self.con.servos[self.servoNum].move()

def startGUI(controller):
    global root 
    root = Tk()

    global app
    app = App(root,controller)
    root.mainloop()
    
    
