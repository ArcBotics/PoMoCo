###############################################################################
# HexSim - Hexapod Simulator
###############################################################################
#
# Notes:
# - All measurement units are in centimeters. If you see say, a leg with a
#    length of '10', thats 10 centimeters, or 100 millimeters
###############################################################################
import math
import threading
import time

from visual import *

from servitorComm import Controller
controller = Controller()
con = True
print "seial controller established"

# simulation parameters
FPS = 60           # max FPS of the 3D animation
#SPEED = 0.1       # speed at which the hexapod moves (0.0-1.0)
                   #  slower movements are smoother, faster more crude/jerky
                   #  because it sends more servo pcommands
SLEEP_TIME = 0.01  # extra time between servo movements, use if program too fast

# hexapod parameters
height = 10.0         # height from middle of hip to floor (cm)

pivotDistance = 10.0 # distance from the center of the body to the hip pivot
pivotAngle = 50      # the angle between legs on a same side of the body

calfLength = 4.7     # legnth of the calf in (cm)
thighLength = 4.7    # length of the thigh (cm)

#setup the window and the scene
#scene.range = 10 # fixed size, no autoscaling
scene.title='PoMoCo - Postion and Motion Controller'
scene.x=100
scene.y=100
scene.width = 800
scene.height = 800
scene.background = (1,1,1)
#scene.stereo = 'redcyan'; scene.stereodepth=2 #dorky 3d-glasses option
floor = box (pos=(0,0,0), length=50, height=0.1, width=50,
             color=color.white)


class leg(threading.Thread):
    def __init__(self,origin=(0,3,0),posRotation=0, name='leg',
                 servos={'hip':-1,'knee':-1,'ankle':-1}):
        threading.Thread.__init__(self)
        #setup leg variables
        self.name = name
        self.posRotation = posRotation
        self.servos = servos

        # setup position of legs
        self.hip_set = self.posRotation
        self.knee_set = 0
        self.ankle_set = 0

        # establish locks for editing hip angles
        self.hipLock = threading.Lock()
        self.kneeLock = threading.Lock()
        self.ankleLock = threading.Lock()

        # setup the hexapod parameters
        self.hipOrigin = origin
        self.thighLength = thighLength
        self.calfLength = calfLength

        # set visual thickness of body parts
        sphereR = 2.5#(self.calfLength+self.thighLength)/2/5
        footR = 2.5#(self.calfLength+self.thighLength)/2/7

        # setup the objects modeled
        self.center_sphere = sphere(pos=self.hipOrigin, radius=sphereR,
                                    color=color.blue)
        self.knee_sphere = sphere(pos=self.center_sphere.pos+
                                  (self.thighLength,0,0), radius=sphereR,
                                  color=color.red)
        self.thighLine=curve(pos=[self.center_sphere.pos, self.knee_sphere.pos],
                             radius=footR,color=color.green)
        self.foot_sphere = sphere(pos=self.knee_sphere.pos+
                                  (self.calfLength,0,0),radius=sphereR,
                                  color=color.orange)
        self.calfLine=curve(pos=[self.knee_sphere.pos, self.foot_sphere.pos],
                            radius=footR,color=color.green)

        label(pos=self.center_sphere.pos, text=self.name, border=0.1, height=0.1)
        # start the thread
        self.start()

    def run(self):
        hip_display = 0
        hip_rotate = 0

        knee_display = 0
        knee_rotate = 0

        ankle_display = 0
        ankle_rotate = 0

        # main 3D scene update loop
        while True:
            rate(FPS)

            self.hipLock.acquire()
            hip_set = self.hip_set+self.posRotation
            self.hipLock.release()

            self.kneeLock.acquire()
            knee_set = self.knee_set
            self.kneeLock.release()

            self.ankleLock.acquire()
            ankle_set = self.ankle_set
            self.ankleLock.release()

            # note: these are all in degrees
            hip_rotate = hip_display-hip_set
            hip_display = hip_set

            knee_rotate = knee_display-knee_set
            knee_display = knee_set

            ankle_rotate = ankle_display-ankle_set
            ankle_display = ankle_set

            # make rotations happen

            # calcualte distance between knee_sphere and foot_sphere relative to
            #  knee_sphere
            knee_foot_diff = self.knee_sphere.pos-self.foot_sphere.pos

            #caluclate rotations for knee_sphere
            self.knee_sphere.rotate(angle=radians(hip_rotate), axis=(0,1,0),
                                    origin=self.center_sphere.pos)
            knee_sphere_axis = (-sin(radians(hip_set)),0,cos(radians(hip_set)))
            self.knee_sphere.rotate(angle=radians(knee_rotate),
                                    axis=knee_sphere_axis,
                                    origin=self.center_sphere.pos)

            # reposition thigh
            self.thighLine.pos=[self.center_sphere.pos, self.knee_sphere.pos]

            # re-apply the distance between knee_sphere and foot_sphere relative
            #  to knee_sphere
            self.foot_sphere.pos = self.knee_sphere.pos-knee_foot_diff

            # reposition calf
            self.calfLine.pos=[self.knee_sphere.pos, self.foot_sphere.pos]

            # rotate foot_sphere to keep it in line with knee_sphere
            self.foot_sphere.rotate(angle=radians(hip_rotate), axis=(0,1,0),
                                    origin=self.knee_sphere.pos)
            foot_sphere_axis = (-sin(radians(hip_set)),0,cos(radians(hip_set)))
            self.foot_sphere.rotate(angle=radians(knee_rotate+ankle_rotate),
                                    axis=foot_sphere_axis,
                                    origin=self.knee_sphere.pos)


    def hipSet(self, degrees=None, uS=None):
        # change the position angle of the hip
        if uS:
            degrees = (uS-1500)/11.111
        self.hipLock.acquire()
        self.hip_set = degrees
        self.hipLock.release()
        # tell controler to move the corresponding servo
        controller.servos[self.servos['hip']].setPos(degrees=degrees)

    def kneeSet(self, degrees=None, uS=None):
        # change the position angle of the knee
        if uS:
            degrees = (uS-1500)/11.111
        if degrees:
            self.kneeLock.acquire()
            self.knee_set = degrees
            self.kneeLock.release()
        # tell controler to move the corresponding servo
        controller.servos[self.servos['knee']].setPos(deg=-degrees)

    def ankleSet(self, degrees=None, uS=None):
        # change the position angle of the ankle
        if uS:
            degrees = (uS-1500)/11.111
        if degrees:
            self.ankleLock.acquire()
            self.ankle_set = degrees
            self.ankleLock.release()
        # tell controler to move the corresponding servo
        controller.servos[self.servos['ankle']].setPos(deg=degrees-90)

    ############################################################################
    #Imported from AutoIK
    ############################################################################

    def setHipDeg(self,endHipAngle,stepTime=1):
        runMovement(self.setHipDeg_function,endHipAngle)

    def setFootY(self,footY,stepTime=1):
        runMovement(self.setFootY_function,footY,stepTime)

    def replantFoot(self,endHipAngle,stepTime=1):
        runMovement(self.replantFoot_function,endHipAngle,stepTime)

    def setHipDeg_function(self,endHipAngle,stepTime=1):
        con.servos[self.hipServoNum].setPos(de=endHipAngle)

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

class hexapod():
    def __init__(self):
        #Legs are defined by short names:
        # RF = Right Front, RM = Right Middle, RB = Right Back
        # LF = Left Front,  LM = Left Middle,  LB = Left Back
        #
        # Right/Left is defined as looking down the hexapod from the behind
        # the head.

        # placement dimensions for the outer legs, i.e. RF,RB,LF,LB
        #  These dimentions are based on a symetric star-shaped hexapod leg layout
        innerX = math.cos(radians(pivotAngle))*pivotDistance
        innerY = math.sin(radians(pivotAngle))*pivotDistance

        # placement dimensions for the outer legs, i.e. LM and RM
        outerX = 1*pivotDistance
        outerY = 0

        # create legs, in their proper positions, and assign servos
        self.RF = leg(origin=(innerX,height,innerY),posRotation=pivotAngle,
                 servos={'hip':0,'knee':1,'ankle':2},name='RF')
        self.RM = leg(origin=(outerX,height,outerY),posRotation=0,
                 servos={'hip':4,'knee':5,'ankle':6},name='RM')
        self.RB = leg(origin=(innerX,height,-innerY),posRotation=-pivotAngle,
                 servos={'hip':8,'knee':9,'ankle':10},name='RB')
        self.LF = leg(origin=(-innerX,height,innerY),posRotation=180-pivotAngle,
                 servos={'hip':16,'knee':17,'ankle':18},name='LF')
        self.LM = leg(origin=(-outerX,height,outerY),posRotation=180,
                 servos={'hip':20,'knee':21,'ankle':22},name='LM')
        self.LB = leg(origin=(-innerX,height,-innerY),posRotation=180+pivotAngle,
                 servos={'hip':24,'knee':25,'ankle':26},name='LB')

        # create the different leg groups
        self.legs = [self.RF,self.RM,self.RB,self.LF,self.LM,self.LB]
        self.tripod1 = [self.RF,self.LM,self.RB]
        self.tripod2 = [self.LF,self.RM,self.LB]

    def moveForward(self):
        pass

    def moveBackward(self):
        pass

    def turnRight(self):
        pass

    def turnLeft(self):
        pass

    def moveStraight(self):
        # setup inital motion variables
        add = 5.0       # defines how fast t
        deg = 0.0       # the current over-all hip movement coordinator
        kneeDeg = 60    # angle knee is at when at footfall. high angle, tall robot
        kneeSwing = 30  # how high the knee swings when raised (in degrees)
        kneeSpeed = 2

        hipSwing = 18   # how wide the hips swing in deg +/-
        hipSpeed = 3

        # set up the inital leg joint positionings
        for leg in self.legs:
            leg.kneeSet(degrees=kneeDeg)
            leg.ankleSet(degrees=90-kneeDeg)

        add = hipSpeed
        for step in range(1000):
            #print "step",step

            # set hip angle, based on side and placement angle
            deg+=add

            self.RF.hipSet(degrees=-deg-pivotAngle/2.0)
            self.RM.hipSet(degrees=deg)
            self.RB.hipSet(degrees=-deg+pivotAngle/2.0)
            self.LF.hipSet(degrees=-deg+pivotAngle/2.0)
            self.LM.hipSet(degrees=deg)
            self.LB.hipSet(degrees=-deg-pivotAngle/2.0)

            # if tripod 1 is forward
            if deg<-hipSwing:
                # move tripod 1 down
                for i in range(0,kneeSwing,kneeSpeed):
                    for leg in self.tripod1:
                        leg.kneeSet(degrees=kneeDeg-kneeSwing+i)
                        leg.ankleSet(degrees=90-leg.knee_set)
                    time.sleep(SLEEP_TIME)
                # move tripod 2 up
                for i in range(0,kneeSwing,kneeSpeed):
                    for leg in self.tripod2:
                        leg.kneeSet(degrees=kneeDeg-i)
                        leg.ankleSet(degrees=90-leg.knee_set)
                    time.sleep(SLEEP_TIME)
                #set the robot to swing tripod 1 back
                add=hipSpeed
                print "end step tripod 1 forward",step

            # if tripod 2 is forward
            if deg>hipSwing:
                # move tripod 2 down
                for i in range(0,kneeSwing,kneeSpeed):
                    for leg in self.tripod2:
                        leg.kneeSet(degrees=kneeDeg-kneeSwing+i)
                        leg.ankleSet(degrees=90-leg.knee_set)
                    time.sleep(SLEEP_TIME)
                # move tripod 1 up
                for i in range(0,kneeSwing,kneeSpeed):
                    for leg in self.tripod1:
                        leg.kneeSet(degrees=kneeDeg-i)
                        leg.ankleSet(degrees=90-leg.knee_set)
                    time.sleep(SLEEP_TIME)
                # set the robot to swing tripod 2 back
                add=-hipSpeed
                print "end step tripod 2 forward",step

            time.sleep(SLEEP_TIME)



if __name__ == '__main__':
    hexy = hexapod()
    time.sleep(3)
    hexy.moveStraight()


