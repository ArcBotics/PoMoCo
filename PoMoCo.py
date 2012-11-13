from Tkinter import *
from tkFileDialog   import askopenfile
from tkFileDialog   import askopenfilename
from tkFileDialog   import asksaveasfile
from tkFileDialog   import asksaveasfilename
import time
import math
import os
import threading
import ConfigParser

import servotorComm
from robot import hexapod
import serial

floor = 60

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

class App:

    def __init__(self, master):
        self.con = servotorComm.Controller() # Servo controller
        self.hexy = hexapod(self.con)
        self.master = master

        self.frame = Frame(self.master)

        self.frame.pack()

        #setup menu system
        menu = Menu(root)
        root.config(menu=menu)
        filemenu = Menu(menu)

        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New")
        filemenu.add_command(label="Save Offsets", command=self.saveOffsets)
        # TODO: bring these over from servitorGui
        #filemenu.add_command(label="Open Offsets", command=self.openOffsets)
        #filemenu.add_command(label="Save Positions", command=self.savePositions)
        #filemenu.add_command(label="Open Positions", command=self.openPositions)

        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quitApp)

        #setup kill button
        self.killButton = Button(self.frame, text="Kill All Servos",fg="red",
                                font=("Helvetica", 20),command=self.gui_estop)
        self.killButton.grid(row=0,column=14)

        self.loadOffsets()

        self.servos = []
        #setup left side, 4 groups of 4 servo controls
        for i in xrange(4):
            self.newServo(0+i*4,[1,8+i*5])
            self.newServo(1+i*4,[1,9+i*5])
            self.newServo(2+i*4,[1,10+i*5])
            self.newServo(3+i*4,[1,11+i*5])
            self.addSpace([0,12+i*5])

        #setup right side, 4 groups of 4 servo controls
        for i in xrange(4):
            self.newServo(16+i*4,[11,8+i*5])
            self.newServo(17+i*4,[11,9+i*5])
            self.newServo(18+i*4,[11,10+i*5])
            self.newServo(19+i*4,[11,11+i*5])
            self.addSpace([11,12+i*5])

        #add some spaces for asthetics
        self.addSpace([10,1])

        # generate buttons for all move functions
        counter = 0
        for move_name in dir(self):
            if "move_" in move_name:
                b = Button(self.frame, text=move_name[5:], command = lambda func=getattr(self, "move_"+move_name[5:]): servotorComm.runMovement(func))
                b.grid(row=counter+8, column=0)
                #b.pack()
                counter += 1

        #servoBars = []

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
        self.estop()
        root.destroy()
        sys.exit()

    def poll(self):
        # Constantly updates the gui based on the current status of the controller

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

        self.master.after(20, self.poll)

    def addSpace(self,coords):
        l2 = Label(self.frame, text="\t\t", fg="red")
        l2.pack()
        l2.grid(row=coords[1], column=coords[0])

    def newServo(self,servoNum,coords):
        self.servos.append(servoGroup(self.frame,self.con,servoNum,colX=coords[0],rowY=coords[1]))

    def gui_estop(self):
        servotorComm.runMovement(self.estop)

    def loadOffsets(self):
        # If there is one offset file in the folder, automatically load it
        off_files = []
        for filename in os.listdir(os.getcwd()):
            start, ext = os.path.splitext(filename)
            if ext == '.cfg':
                off_files.append(filename)

        if len(off_files) == 1:
            print "opening",off_files[0]
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
                print "automatically loaded offsets from",off_files[0]
            except:
                print "automatic offset load failed, is there an offset file in the program directory?"

    def estop(self):
        self.con.killAll()

    def move_reset(self):
        deg = -30
        #put all the feet centered and on the floor.
        self.hexy.RF.replantFoot(deg,stepTime=0.3)
        self.hexy.LM.replantFoot(1,stepTime=0.3)
        self.hexy.RB.replantFoot(-deg,stepTime=0.3)
        time.sleep(0.5)
        self.hexy.LF.replantFoot(-deg,stepTime=0.3)
        self.hexy.RM.replantFoot(1,stepTime=0.3)
        self.hexy.LB.replantFoot(deg,stepTime=0.3)
        time.sleep(0.5)

    def move_rotateLeft(self):
        deg = 40

        #set neck to where body is turning
        self.hexy.neck.set(deg)

        #re-plant tripod2 deg degrees forward
        for leg in self.hexy.tripod2:
            leg.replantFoot(deg,stepTime=0.2)
        time.sleep(0.3)

        #raise tripod1 feet
        for leg in self.hexy.tripod1:
            leg.setFootY(int(floor/2.0))
        time.sleep(0.3)

        #swing tripod2 feet back 2*deg degrees (to -deg)
        for leg in self.hexy.tripod2:
            leg.setHipDeg(-deg,stepTime=0.3)

        #reset neck as body turns
        self.hexy.neck.set(0)
        time.sleep(0.4)

        #lower tripod1 feet
        for leg in self.hexy.tripod1:
            leg.setFootY(floor)
        time.sleep(0.3)

        #re-plant tripod2 deg degrees to starting position
        for leg in self.hexy.tripod2:
            leg.replantFoot(0,stepTime=0.3)
        time.sleep(0.3)

    def move_rotateRight(self):
        deg = -40

        #set neck to where body is turning
        self.hexy.neck.set(deg)

        #re-plant tripod1 deg degrees forward
        for leg in self.hexy.tripod1:
            leg.replantFoot(deg,stepTime=0.2)
        time.sleep(0.5)

        #raise tripod2 feet in place as tripod1 rotate and neck
        for leg in self.hexy.tripod2:
            leg.setFootY(int(floor/2.0))
        time.sleep(0.3)

        #swing tripod1 feet back 2*deg degrees (to -deg)
        for leg in self.hexy.tripod1:
            leg.setHipDeg(-deg,stepTime=0.3)

        #reset neck as body turns
        self.hexy.neck.set(0)
        time.sleep(0.4)

        #lower tripod2 feet
        for leg in self.hexy.tripod2:
            leg.setFootY(floor)
        time.sleep(0.3)

        #re-plant tripod1 deg degrees to starting position
        for leg in self.hexy.tripod1:
            leg.replantFoot(0,stepTime=0.3)
        time.sleep(0.3)

    def move_moveForward(self):
        deg = 25
        midFloor = 30
        hipSwing = 25
        pause = 0.5

        #tripod1 = RF,LM,RB
        #tripod2 = LF,RM,LB

        for timeStop in range(2):
            #time.sleep(0.1)
            # replant tripod2 forward while tripod1 move behind
            #   relpant tripod 2 forward
            self.hexy.LF.replantFoot(deg-hipSwing,stepTime=0.5)
            self.hexy.RM.replantFoot(hipSwing,stepTime=0.5)
            self.hexy.LB.replantFoot(-deg-hipSwing,stepTime=0.5)

            #   tripod1 moves behind
            self.hexy.RF.setHipDeg(-deg-hipSwing,stepTime=0.5)
            self.hexy.LM.setHipDeg(hipSwing,stepTime=0.5)
            self.hexy.RB.setHipDeg(deg-hipSwing,stepTime=0.5)
            time.sleep(0.6)

            # replant tripod1 forward while tripod2 move behind
            #   replant tripod1 forward
            self.hexy.RF.replantFoot(-deg+hipSwing,stepTime=0.5)
            self.hexy.LM.replantFoot(-hipSwing,stepTime=0.5)
            self.hexy.RB.replantFoot(deg+hipSwing,stepTime=0.5)

            #   tripod2 moves behind
            self.hexy.LF.setHipDeg(deg+hipSwing,stepTime=0.5)
            self.hexy.RM.setHipDeg(-hipSwing,stepTime=0.5)
            self.hexy.LB.setHipDeg(-deg+hipSwing,stepTime=0.5)
            time.sleep(0.6)

    def move_moveBackward(self):
        print "moving backward"
        deg = -25
        midFloor = 30
        hipSwing = 25
        pause = 0.5

        #tripod1 = RF,LM,RB
        #tripod2 = LF,RM,LB

        for timeStop in range(2):
            #time.sleep(0.1)
            # replant tripod2 backwards while tripod1 moves forward
            #   relpant tripod 2 backwards
            self.hexy.LF.replantFoot(deg+hipSwing,stepTime=0.5)
            self.hexy.RM.replantFoot(-hipSwing,stepTime=0.5)
            self.hexy.LB.replantFoot(-deg+hipSwing,stepTime=0.5)

            #   tripod1 moves forward
            self.hexy.RF.setHipDeg(-deg+hipSwing,stepTime=0.5)
            self.hexy.LM.setHipDeg(-hipSwing,stepTime=0.5)
            self.hexy.RB.setHipDeg(deg+hipSwing,stepTime=0.5)
            time.sleep(0.6)

            # replant tripod1 backwards while tripod2 moves behind
            #   replant tripod1 backwards
            self.hexy.RF.replantFoot(-deg-hipSwing,stepTime=0.5)
            self.hexy.LM.replantFoot(hipSwing,stepTime=0.5)
            self.hexy.RB.replantFoot(deg-hipSwing,stepTime=0.5)

            #   tripod2 moves behind
            self.hexy.LF.setHipDeg(deg-hipSwing,stepTime=0.5)
            self.hexy.RM.setHipDeg(hipSwing,stepTime=0.5)
            self.hexy.LB.setHipDeg(-deg-hipSwing,stepTime=0.5)
            time.sleep(0.6)

    def move_point(self):
        self.hexy.neck.set(0)
        time.sleep(1)
        self.hexy.neck.set(30)
        time.sleep(1)
        self.hexy.RF.knee(-60)
        self.hexy.RF.ankle(-40)
        time.sleep(0.2)
        self.hexy.RF.hip(20)
        time.sleep(0.3)
        self.hexy.RF.hip(50)
        time.sleep(0.3)
        self.hexy.RF.hip(10)
        time.sleep(1)
        self.hexy.neck.set(0)

    def move_leanBack(self):

        # Pick up back feet
        self.hexy.RB.setHipDeg(45,stepTime=0.3)
        self.hexy.LB.setHipDeg(-45,stepTime=0.3)
        self.hexy.RB.setFootY(40)
        self.hexy.LB.setFootY(40)
        # Push side feet down
        self.hexy.RM.setFootY(70)
        self.hexy.LM.setFootY(70)
        time.sleep(0.2)

        # Put hands into air
        self.hexy.LF.hip(45)
        self.hexy.LF.knee(0)
        self.hexy.LF.ankle(0)
        self.hexy.RF.hip(-45)
        self.hexy.RF.knee(0)
        self.hexy.RF.ankle(0)
        time.sleep(0.4)

    def move_leanBackToReset(self):

        # Put front feet back down
        print "Put hands into air"
        self.hexy.RF.setHipDeg(30,stepTime=0.1)
        self.hexy.LF.setHipDeg(-30,stepTime=0.1)
        self.hexy.RF.setFootY(floor)
        self.hexy.LF.setFootY(floor)
        time.sleep(0.1)

        # Reset back feet back down
        self.hexy.RB.setHipDeg(30,stepTime=0.1)
        self.hexy.LB.setHipDeg(-30,stepTime=0.1)
        self.hexy.RB.setFootY(floor)
        self.hexy.LB.setFootY(floor)

        # Pull side feet back up
        print "Push side feet down"
        self.hexy.RM.setFootY(floor)
        self.hexy.LM.setFootY(floor)
        time.sleep(0.2)

        self.move_reset()

    def move_setZero(self):
        for servo in self.con.servos:
            self.con.servos[servo].setPos(deg=0)

    def move_tiltLeft(self):
        self.hexy.LF.setFootY(0)
        self.hexy.LM.setFootY(-10)
        self.hexy.LB.setFootY(0)

        self.hexy.RF.setFootY(75)
        self.hexy.RM.setFootY(75)
        self.hexy.RB.setFootY(75)

    def move_tiltRight(self):
        self.hexy.LF.setFootY(75)
        self.hexy.LM.setFootY(75)
        self.hexy.LB.setFootY(75)

        self.hexy.RF.setFootY(0)
        self.hexy.RM.setFootY(-10)
        self.hexy.RB.setFootY(0)

    def move_tiltReset(self):
        self.hexy.LF.setFootY(floor)
        self.hexy.LM.setFootY(floor)
        self.hexy.LB.setFootY(floor)

        self.hexy.RF.setFootY(floor)
        self.hexy.RM.setFootY(floor)
        self.hexy.RB.setFootY(floor)

    def move_tiltForward(self):
        self.hexy.LF.setFootY(floor/4)
        self.hexy.LM.setFootY(floor/2)
        self.hexy.LB.setFootY(floor)

        self.hexy.RF.setFootY(floor/4)
        self.hexy.RM.setFootY(floor/2)
        self.hexy.RB.setFootY(floor)

    def move_tiltBackward(self):
        self.hexy.LF.setFootY(floor)
        self.hexy.LM.setFootY(floor/2)
        self.hexy.LB.setFootY(floor/4)

        self.hexy.RF.setFootY(floor)
        self.hexy.RM.setFootY(floor/2)
        self.hexy.RB.setFootY(floor/4)

    def move_killAllHumans(self):
        # tilt forward
        self.move_tiltForward()

        time.sleep(0.3)

        #prep paw
        self.hexy.LF.hip(-40)
        self.hexy.LF.knee(0)
        self.hexy.LF.ankle(0)

        time.sleep(0.3)

        #swipe paw
        self.hexy.LF.hip(60)

        time.sleep(0.3)

        #set paw down
        self.hexy.LF.ankle(-60)

        time.sleep(0.3)

        #swing other paw
        self.hexy.RF.hip(40)
        self.hexy.RF.knee(0)
        self.hexy.RF.ankle(0)

        time.sleep(0.3)

        #swipe paw
        self.hexy.RF.hip(-60)

    def move_dance(self):
        self.move_tiltLeft()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)
        self.move_tiltRight()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)

        self.move_tiltLeft()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)
        self.move_tiltRight()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)

        self.move_tiltForward()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)
        self.move_tiltBackward()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)

        self.move_tiltForward()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)
        self.move_tiltBackward()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)

    def move_bellyFlop(self):
        self.move_setZero()
        time.sleep(2)
        self.move_tiltRight()
        self.move_tiltLeft()
        time.sleep(0.3)
        self.move_tiltReset()
        time.sleep(0.5)
        self.move_reset()

    def move_danceCircle(self):
        self.move_tiltLeft()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)
        self.move_tiltForward()
        time.sleep(0.2)
        self.move_tiltReset()
        time.sleep(0.2)
        self.move_tiltRight()
        time.sleep(0.2)

    def move_wave(self):
        self.hexy.neck.set(0)

        self.hexy.LF.hip(-20)
        self.hexy.LF.knee(0)
        self.hexy.LF.ankle(0)

        time.sleep(0.2)

        for i in range(3):
            self.hexy.LF.hip(-20)
            self.hexy.LF.knee(-50)
            self.hexy.LF.ankle(-20)

            time.sleep(0.2)

            self.hexy.LF.knee(-10)
            self.hexy.LF.ankle(0)
            time.sleep(0.2)

        self.hexy.LF.knee(-40)

    def move_typing(self):
        self.move_leanBack()
        time.sleep(0.3)

        for i in range(10):
            self.hexy.RF.knee(0)
            self.hexy.LF.knee(60)

            time.sleep(0.3)

            self.hexy.RF.knee(60)
            self.hexy.LF.knee(0)

            time.sleep(0.3)

    def move_demo(self):
        self.move_reset()
        time.sleep(0.3)
        self.move_tiltForward()
        time.sleep(0.3)
        self.move_tiltReset()
        time.sleep(0.3)
        self.move_tiltBackward()
        time.sleep(0.3)
        self.move_tiltReset()
        time.sleep(0.3)
        self.move_tiltRight()
        time.sleep(0.3)
        self.move_tiltReset()
        time.sleep(0.3)
        self.move_tiltLeft()
        time.sleep(0.3)
        self.move_tiltReset()
        time.sleep(0.3)
        self.move_moveForward()
        time.sleep(0.2)
        self.move_moveBackward()
        time.sleep(0.2)
        self.move_reset()
        time.sleep(0.2)
        self.move_rotateLeft()
        time.sleep(0.2)
        self.move_rotateLeft()
        time.sleep(0.2)
        self.move_rotateRight()
        time.sleep(0.2)
        self.move_rotateRight()


if __name__ == '__main__':

    root = Tk()

    app = App(root)

    root.mainloop()

