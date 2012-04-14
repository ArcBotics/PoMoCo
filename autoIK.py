from Tkinter import *
import time
import math
import serial
from servotorComm import Controller
import threading

h=500
w=500

cF=5 #endpoint circle radii (pixels)
con = Controller()
floor = 60

#modifies how smoothly the servos move
#smoother means more processing power, and fills the serial line
#lower if movements start to slow down, or get weird
#Anything higher than 50 is pointless (maximum refresh of standard servos)
stepPerS = 50

class hexapod():

    def __init__(self):
        self.RF = leg('frontRight',0,1,2)
        self.RM   = leg('midRight',4,5,6)
        self.RB  = leg('backRight',8,9,10)

        self.LF  = leg('frontLeft',16,17,18)
        self.LM    = leg('midLeft',20,21,22)
        self.LB   = leg('backLeft',24,25,26)

        self.legs = [self.RF,
                     self.RM,
                     self.RB,
                     self.LF,
                     self.LM,
                     self.LB]

        self.neck = 31

        self.tripod1 = [self.RF,self.RB,self.LM]
        self.tripod2 = [self.LF,self.LB,self.RM]


class runMovement(threading.Thread):

    def __init__(self,function,*args):
        threading.Thread.__init__(self)
        self.function=function
        self.args = args
        self.start()

    def run(self):
        self.function(*self.args)

class leg():

    def __init__(self,name,hipServoNum,kneeServoNum,ankleServoNum,simOrigin=(0,3,0)):
        self.name = name
        self.hipServoNum = hipServoNum
        self.kneeServoNum = kneeServoNum
        self.ankleServoNum = ankleServoNum

    def setHipDeg(self,endHipAngle,stepTime=1):
        runMovement(self.setHipDeg_function,endHipAngle,stepTime)

    def setFootY(self,footY,stepTime=1):
        runMovement(self.setFootY_function,footY,stepTime)

    def replantFoot(self,endHipAngle,stepTime=1):
        runMovement(self.replantFoot_function,endHipAngle,stepTime)

    def setHipDeg_function(self,endHipAngle,stepTime):
        currentHipAngle = con.servos[self.hipServoNum].getPosDeg()
        hipMaxDiff = endHipAngle-currentHipAngle

        steps = range(int(stepPerS))
        for i,t in enumerate(steps):
            hipAngle = (hipMaxDiff/len(steps))*(i+1)
            try:
                anglNorm=hipAngle*(180/(hipMaxDiff))
            except:
                anglNorm=hipAngle*(180/(1))
            hipAngle = currentHipAngle+hipAngle
            con.servos[self.hipServoNum].setPos(degrees=hipAngle)

            #wait for next cycle
            time.sleep(stepTime/float(stepPerS))

    def setFootY_function(self,footY,stepTime):
        # TODO: max steptime dependent
        #print self.hipServoNum,""
        if (footY < 75) and (footY > -75):
            kneeAngle = math.degrees(math.asin(float(footY)/75.0))
            ankleAngle = 90-kneeAngle

            con.servos[self.kneeServoNum].setPos(degrees=-kneeAngle)
            con.servos[self.ankleServoNum].setPos(degrees=ankleAngle-90)

    def replantFoot_function(self,endHipAngle,stepTime):
    #smoothly moves a foot from one position on the ground to another in time seconds
        currentHipAngle = con.servos[self.hipServoNum].getPosDeg()

        hipMaxDiff = endHipAngle-currentHipAngle

        steps = range(int(stepPerS))
        for i,t in enumerate(steps):

            hipAngle = (hipMaxDiff/len(steps))*(i+1)
            #print "hip angle calc'd:",hipAngle

            #calculate the absolute distance between the foot's highest and lowest point
            footMax = 0
            footMin = floor
            footRange = abs(footMax-footMin)

            #normalize the range of the hip movement to 180 deg
            try:
                anglNorm=hipAngle*(180/(hipMaxDiff))
            except:
                anglNorm=hipAngle*(180/(1))
            #print "normalized angle:",anglNorm

            #base footfall on a sin pattern from footfall to footfall with 0 as the midpoint
            footY = footMin-math.sin(math.radians(anglNorm))*footRange
            #print "calculated footY",footY

            #set foot height
            self.setFootY(footY,stepTime=0)
            hipAngle = currentHipAngle+hipAngle
            con.servos[self.hipServoNum].setPos(degrees=hipAngle)

            #wait for next cycle
            time.sleep(stepTime/float(stepPerS))

class App:

    def __init__(self, master):
        self.hexy = hexapod()

        frame = Frame(master)

        frame.pack()
        #sets the bottom 'floor' Y value the legs will rest on
        self.floor = IntVar()
        self.floor.set(60)

        self.winX=500 #frame size in pixels
        self.winY=500 #frame size in pixels

        self.rotateRightButton = Button(frame, text="Rotate Right",command=self.rotateRight)
        self.rotateRightButton.grid(row=0, column=3)

        self.rotateLeftButton = Button(frame, text="Rotate Left",command=self.rotateLeft)
        self.rotateLeftButton.grid(row=0, column=2)

        self.moveForwardButton = Button(frame, text="Move Forward",command=self.moveForward)
        self.moveForwardButton.grid(row=1, column=2)

        self.moveBackwardButton = Button(frame, text="Move Backward",command=self.moveBackward)
        self.moveBackwardButton.grid(row=1, column=3)

        self.resetButton = Button(frame, text="Reset",command=self.reset)
        self.resetButton.grid(row=2, column=3)

        self.resetButton = Button(frame, text="E-Stop",command=self.estop)
        self.resetButton.grid(row=2, column=4)


    def rotateRight(self):
        deg = 40
        #self.reset()

        #set neck to where body is turning
        con.servos[self.hexy.neck].setPos(degrees=-deg)

        #re-plant tripod2 deg degrees forward
        for leg in self.hexy.tripod2:
            leg.replantFoot(deg,stepTime=0.4)
        time.sleep(0.5)

        #raise tripod1 feet
        for leg in self.hexy.tripod1:
            leg.setFootY(int(floor/2.0))
        time.sleep(0.3)

        #swing tripod2 feet back 2*deg degrees (to -deg)
        for leg in self.hexy.tripod2:
            leg.setHipDeg(-deg,stepTime=0.3)

        #reset neck as body turns
        con.servos[self.hexy.neck].setPos(degrees=0)
        time.sleep(0.4)

        #lower tripod1 feet
        for leg in self.hexy.tripod1:
            leg.setFootY(floor)
        time.sleep(0.3)

        #re-plant tripod2 deg degrees to starting position
        for leg in self.hexy.tripod2:
            leg.replantFoot(0,stepTime=0.3)
        time.sleep(0.3)

    def rotateLeft(self):
        deg = -40
        #self.reset()

        #set neck to where body is turning
        con.servos[self.hexy.neck].setPos(degrees=-deg)

        #re-plant tripod1 deg degrees forward
        for leg in self.hexy.tripod1:
            leg.replantFoot(deg,stepTime=0.4)
        time.sleep(0.5)

        #raise tripod2 feet in place as tripod1 rotate and neck
        for leg in self.hexy.tripod2:
            leg.setFootY(int(floor/2.0))
        time.sleep(0.3)

        #swing tripod1 feet back 2*deg degrees (to -deg)
        for leg in self.hexy.tripod1:
            leg.setHipDeg(-deg,stepTime=0.3)

        #reset neck as body turns
        con.servos[self.hexy.neck].setPos(degrees=0)
        time.sleep(0.4)

        #lower tripod2 feet
        for leg in self.hexy.tripod2:
            leg.setFootY(floor)
        time.sleep(0.3)

        #re-plant tripod1 deg degrees to starting position
        for leg in self.hexy.tripod1:
            leg.replantFoot(0,stepTime=0.3)
        time.sleep(0.3)

    def moveForward(self):
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
            time.sleep(1.0)

            # replant tripod1 forward while tripod2 move behind
            #   replant tripod1 forward
            self.hexy.RF.replantFoot(-deg+hipSwing,stepTime=0.5)
            self.hexy.LM.replantFoot(-hipSwing,stepTime=0.5)
            self.hexy.RB.replantFoot(deg+hipSwing,stepTime=0.5)

            #   tripod2 moves behind
            self.hexy.LF.setHipDeg(deg+hipSwing,stepTime=0.5)
            self.hexy.RM.setHipDeg(-hipSwing,stepTime=0.5)
            self.hexy.LB.setHipDeg(-deg+hipSwing,stepTime=0.5)
            time.sleep(1.0)

    def moveBackward(self):
        print "moving backward"
        deg = 25
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
            time.sleep(0.5)

            # replant tripod1 backwards while tripod2 moves behind
            #   replant tripod1 backwards
            self.hexy.RF.replantFoot(-deg-hipSwing,stepTime=0.5)
            self.hexy.LM.replantFoot(hipSwing,stepTime=0.5)
            self.hexy.RB.replantFoot(deg-hipSwing,stepTime=0.5)

            #   tripod2 moves behind
            self.hexy.LF.setHipDeg(deg-hipSwing,stepTime=0.5)
            self.hexy.RM.setHipDeg(hipSwing,stepTime=0.5)
            self.hexy.LB.setHipDeg(-deg-hipSwing,stepTime=0.5)
            time.sleep(0.5)

    def reset(self):
        deg = 30
        #put all the feet centered and on the floor.
        self.hexy.RF.replantFoot(-deg,stepTime=0.3)
        self.hexy.LM.replantFoot(1,stepTime=0.3)
        self.hexy.RB.replantFoot(deg,stepTime=0.3)
        time.sleep(1.0)
        self.hexy.LF.replantFoot(deg,stepTime=0.3)
        self.hexy.RM.replantFoot(1,stepTime=0.3)
        self.hexy.LB.replantFoot(-deg,stepTime=0.3)
        time.sleep(1.0)


    def estop(self):
        #con.killAll()
        deg = 50
        for i in range(5):
            self.hexy.RF.setHipDeg(deg,stepTime=1.0)
            time.sleep(1)
            self.hexy.RF.setHipDeg(-deg,stepTime=0.5)
            time.sleep(0.5)

if __name__ == '__main__':

    root = Tk()

    app = App(root)

    root.mainloop()

