from Tkinter import *
import time
import math
import serial
from ServitorComm import Controller
import threading
import hexSim

h=500
w=500

cF=5 #endpoint circle radii (pixels)
con = Controller()
floor = 60

class hexapod():

    def __init__(self):
        self.frontRight = leg('frontRight',0,1,2)
        self.midRight   = leg('midRight',4,5,6)
        self.backRight  = leg('backRight',8,9,10)

        self.frontLeft  = leg('frontLeft',16,17,18)
        self.midLeft    = leg('midLeft',20,21,22)
        self.backLeft   = leg('backLeft',24,25,26)

        self.legs = [self.frontRight,
                     self.midRight,
                     self.backRight,
                     self.frontLeft,
                     self.midLeft,
                     self.backLeft]

        self.neck = 31

        self.tripod1 = [self.frontRight,self.backRight,self.midLeft]
        self.tripod2 = [self.frontLeft,self.backLeft,self.midRight]


class runMovement(threading.Thread):

    def __init__(self,function,*args):
        threading.Thread.__init__(self)
        self.function=function
        self.args = args
        #print self.function
        #print self.args
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
        runMovement(self.setHipDeg_function,endHipAngle)

    def setFootY(self,footY,stepTime=1):
        runMovement(self.setFootY_function,footY,stepTime)

    def replantFoot(self,endHipAngle,stepTime=1):
        runMovement(self.replantFoot_function,endHipAngle,stepTime)

    def setHipDeg_function(self,endHipAngle,stepTime=1):
        con.servos[self.hipServoNum].setPos(degrees=endHipAngle)

    def setFootY_function(self,footY,stepTime):
        #print self.hipServoNum,""
        if (footY < 75) and (footY > -75):
            kneeAngle = math.degrees(math.asin(float(footY)/75.0))
            ankleAngle = 90-kneeAngle

            con.servos[self.kneeServoNum].setPos(degrees=-kneeAngle)
            con.servos[self.ankleServoNum].setPos(degrees=ankleAngle-90)

    def replantFoot_function(self,endHipAngle,stepTime):
    #smoothly moves a foot from one position on the ground to another in time seconds
        currentHipAngle = con.servos[self.hipServoNum].getPosDeg()
        #print "current hip angle:",currentHipAngle
        #print "end hip angle:",endHipAngle
        hipMaxDiff = endHipAngle-currentHipAngle

        steps = range(20)
        for i,t in enumerate(steps):

            hipAngle = (hipMaxDiff/len(steps))*(i+1)
            #print "hip angle calc'd:",hipAngle

            #calculate the absolute distance between the foot's highest and lowest point
            footMax = 0
            footMin = floor
            footRange = abs(footMax-footMin)

            #normalize the range of the hip movement to 180 deg
            anglNorm=hipAngle*(180/(hipMaxDiff))
            #print "normalized angle:",anglNorm

            #base footfall on a sin pattern from footfall to footfall with 0 as the midpoint
            footY = footMin-math.sin(math.radians(anglNorm))*footRange
            #print "calculated footY",footY

            #set foot height
            self.setFootY(footY)
            hipAngle = currentHipAngle+hipAngle
            con.servos[self.hipServoNum].setPos(degrees=hipAngle)

            #wait for next cycle
            time.sleep(stepTime/20.0)

class App:

    def __init__(self, master):
        self.hexy = hexapod()
        self.simLeg = hexSim.leg()

        frame = Frame(master)

        frame.pack()
        #sets the bottom 'floor' Y value the legs will rest on
        self.floor = IntVar()
        self.floor.set(60)

        self.angle = DoubleVar() #angle in degrees in float from 0-360
        self.angle.set(0)
        self.distance = DoubleVar() #distance in precent of frame in float, from 0-1.0
        self.distance.set(0.3)
        self.angle2 = DoubleVar() #angle in degrees in float from 0-360
        self.angle2.set(0)
        self.angle3 = DoubleVar() #angle in degrees in float from 0-360
        self.angle3.set(0)
        self.distance2 = DoubleVar() #distance in precent of frame in float, from 0-1.0
        self.distance2.set(0.3)
        self.winX=500 #frame size in pixels
        self.winY=500 #frame size in pixels
        self.center=[self.winX/2,self.winY/2] #coordinates of the box center
        self.hipKneeIK = IntVar() #serial link is active/inactive

        self.serialActiveCheckbox = Checkbutton(frame, text="Hip-Knee IK", variable=self.hipKneeIK)
        self.serialActiveCheckbox.grid(row=0,column=1)

        self.header = Label(frame,text="Display Degree in Box")
        self.header.grid(row=0,column=0)

        #self.testFunctionButton = Button(frame, text="Test Movement",command=self.testMovement)
        #self.testFunctionButton.grid(row=0, column=4)

        self.rotateRightButton = Button(frame, text="Rotate Right",command=self.rotateRight)
        self.rotateRightButton.grid(row=0, column=3)

        self.rotateLeftButton = Button(frame, text="Rotate Left",command=self.rotateLeft)
        self.rotateLeftButton.grid(row=0, column=2)

        self.posScale = Scale(frame, from_=-360.0, to=360.0,  resolution=0.1, length=360,
                                orient=HORIZONTAL,variable=self.angle,command=self.updateLine)
        self.posScale.grid(row=1,column=0)

        self.distScale = Scale(frame, from_=0.0, to=1.0, resolution=0.01, length=360,
                                orient=HORIZONTAL,variable=self.distance,command=self.updateLine)
        self.distScale.grid(row=2,column=0)

        self.pos2Scale = Scale(frame, from_=-360.0, to=360.0,  resolution=0.1, length=360,
                                orient=HORIZONTAL,variable=self.angle2,command=self.updateLine)
        self.pos2Scale.grid(row=3,column=0)

        self.dist2Scale = Scale(frame, from_=0.0, to=1.0, resolution=0.01, length=360,
                                orient=HORIZONTAL,variable=self.distance2,command=self.updateLine)
        self.dist2Scale.grid(row=4,column=0)

        #setup hip angle controls
        self.pos3Scale = Scale(frame, from_=-360.0, to=360.0,  resolution=0.1, length=360,
                                orient=HORIZONTAL,variable=self.angle3,command=self.updateLine)
        self.pos3Scale.grid(row=1,column=1)

        #create knee-angle movement box
        self.drawingSpace = Canvas(frame, width=self.winX, height=self.winX)
        self.drawingSpace.config(bg="white")
        self.drawingSpace.grid(row=6, column=0)

        #create box border
        self.drawingSpace.create_line(2, 2, self.winX-1, 2)
        self.drawingSpace.create_line(2, 2, 2, self.winY-1)
        self.drawingSpace.create_line(self.winX-1, self.winY-1, self.winX-1, 1)
        self.drawingSpace.create_line(self.winX-1, self.winY-1, 1, self.winY-1)

        #bind mouse clicks to box
        self.drawingSpace.bind("<B1-Motion>", self.mouseClick1)

    def updateLine(self,*args):
        angle = float(self.angle.get())
        distance = float(self.distance.get())
        self.simLeg.hipSet(float(self.angle3.get()))
        self.simLeg.kneeSet(float(self.angle.get()))
        self.simLeg.ankleSet(float(self.angle2.get()))

        if angle < 0:
            angle = 360+angle

        angle2 = float(self.angle2.get())+angle
        distance2 = float(self.distance2.get())

        if angle2 < 0:
            angle2 = 360+angle2

        #determine line orgin
        x1=math.cos(math.radians(angle))*0.5*distance*self.winX+self.center[0]
        y1=math.sin(math.radians(angle))*0.5*distance*self.winY+self.center[1]

        x2=math.cos(math.radians(angle2))*0.5*distance2*self.winX+x1
        y2=math.sin(math.radians(angle2))*0.5*distance2*self.winY+y1

        #draw the start line marker circle
        try:
            self.drawingSpace.delete(self.start)
        except:
            pass
        self.start = self.drawingSpace.create_oval(x1-cF,y1-cF,x1+cF,y1+cF,fill="white")

        #draw the line
        try:
            self.drawingSpace.delete(self.line1)
        except:
            pass
        self.line1 = self.drawingSpace.create_line(x1,y1,self.center[0],self.center[1],fill="red")

        #draw the line2
        try:
            self.drawingSpace.delete(self.line2)
        except:
            pass
        self.line2 = self.drawingSpace.create_line(x2,y2,x1,y1,fill="red")

    def mouseClick1(self, event):
        x=event.x
        y=event.y

        #subtract center
        x=x-self.center[0]
        y=-y+self.center[1]

        if (x==0) and (y>0):
            angle=0.0
        if (x==0) and (y<0):
            angle=180.0
        if (x<0) and (y==0):
            angle=270.0
        if (x>0) and (y==0):
            angle=90.0

        if x!=0 and y!=0:
            angle = math.degrees(math.atan(float(y)/float(x)))
            if (x>0):
                angle=90-angle
            if (x<0):
                angle=270-angle

        kneeY = -y-75
        print "kneeY",kneeY
        self.hexy.frontLeft.setFootY(kneeY)

        self.updateLine()

    def rotateRight(self):
        deg = 60
        midFloor = 30

        #put all the feet centered and on the floor.
        for leg in self.hexy.legs:
            leg.setHipDeg(1)
            leg.setFootY(floor)
        time.sleep(0.5)

        #set neck to where body is turning
        con.servos[self.hexy.neck].setPos(degrees=-50)

        #re-plant tripod1 deg degrees forward
        for leg in self.hexy.tripod1:
            leg.replantFoot(deg,stepTime=0.3)
        time.sleep(1)

        #raise tripod2 feet
        for leg in self.hexy.tripod2:
            leg.setFootY(midFloor)
        time.sleep(0.3)

        #swing tripod1 feet back 2*deg degrees (to -deg)
        for leg in self.hexy.tripod1:
            leg.setHipDeg(-deg)
        time.sleep(0.5)

        #reset neck as body turns
        con.servos[self.hexy.neck].setPos(degrees=0)

        #lower tripod2 feet
        for leg in self.hexy.tripod2:
            leg.setFootY(floor)
        time.sleep(0.3)

        #re-plant tripod1 deg degrees to starting position
        for leg in self.hexy.tripod1:
            leg.replantFoot(0,stepTime=0.3)
        time.sleep(1)

    def rotateLeft(self):
        deg = 60
        midFloor = 30

        #put all the feet centered and on the floor.
        for leg in self.hexy.legs:
            leg.setHipDeg(1)
            leg.setFootY(floor)
        time.sleep(0.5)

        #set neck to where body is turning
        con.servos[self.hexy.neck].setPos(degrees=50)

        #re-plant tripod2 deg degrees backwards
        for leg in self.hexy.tripod2:
            leg.replantFoot(-deg,stepTime=0.5)
        time.sleep(1)

        #raise tripod1 feet
        for leg in self.hexy.tripod1:
            leg.setFootY(midFloor)
        time.sleep(0.3)

        #swing tripod2 feet forward 2*deg degrees (to deg)
        for leg in self.hexy.tripod2:
            leg.setHipDeg(deg)
        time.sleep(0.5)

        #reset neck as body turns
        con.servos[self.hexy.neck].setPos(degrees=0)

        #lower tripod1 feet
        for leg in self.hexy.tripod1:
            leg.setFootY(floor)
        time.sleep(0.3)

        #re-plant tripod2 deg degrees to starting position
        for leg in self.hexy.tripod2:
            leg.replantFoot(0,stepTime=0.5)
        time.sleep(1)

if __name__ == '__main__':

    root = Tk()

    app = App(root)

    root.mainloop()

