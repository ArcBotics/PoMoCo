from visual import *
import math
import threading
import time

#setup the window and the scene
scene.range = 10 # fixed size, no autoscaling
scene.title='Hexapod Simulator'
scene.x=100
scene.y=100
scene.width = 400
scene.height = 400
scene.background = (1,1,1)
#scene.stereo = 'redcyan'

class leg(threading.Thread):
    def __init__(self,origin=(0,3,0)):
        threading.Thread.__init__(self)

        self.hip_set = 0
        self.knee_set = 0
        self.ankle_set = 0

        #establish locks for editing hip angles
        self.hipLock = threading.Lock()
        self.kneeLock = threading.Lock()
        self.ankleLock = threading.Lock()

        #setup the hexapod parameters
        self.hipOrigin = origin
        self.thighLength = 2.0
        self.calfLength = 2.0

        #setup the objects modeled
        self.floor = box (pos=(0,0,0), length=20, height=0.1, width=20, color=color.white)

        self.center_sphere = sphere(pos=self.hipOrigin, radius=0.3, color=color.blue)

        self.thigh = box(pos=self.center_sphere.pos+(self.thighLength/2.0,0,0),
                         length=self.thighLength, height=0.2, width=0.2, color=color.green)
        self.knee_sphere = sphere(pos=self.center_sphere.pos+(self.thighLength,0,0),
                                  radius=0.3, color=color.red)

        self.calf = box(pos=self.knee_sphere.pos+(self.calfLength/2.0,0,0),
                        length=self.calfLength, height=0.2, width=0.2, color=color.black)

        self.foot_sphere = sphere(pos=self.knee_sphere.pos+(self.calfLength,0,0), radius=0.3,
                                  color=color.orange)

        self.start()

    def run(self):
        hip_display = 0
        hip_rotate = 0

        knee_display = 0
        knee_rotate = 0

        ankle_display = 0
        ankle_rotate = 0

        #main scene update loop
        while True:
            rate(25)

            self.hipLock.acquire()
            hip_set = self.hip_set
            self.hipLock.release()

            self.kneeLock.acquire()
            knee_set = self.knee_set
            self.kneeLock.release()

            self.ankleLock.acquire()
            ankle_set = self.ankle_set
            self.ankleLock.release()



            #note: these are all in degrees
            hip_rotate = hip_display-hip_set
            hip_display = hip_set

            knee_rotate = knee_display-knee_set
            knee_display = knee_set

            ankle_rotate = ankle_display-ankle_set
            ankle_display = ankle_set

            ##make rotations happen

            #calcualte distance between knee_sphere and foot_sphere relative to knee_sphere
            knee_calf_diff = self.knee_sphere.pos-self.calf.pos
            knee_foot_diff = self.knee_sphere.pos-self.foot_sphere.pos


            #caluclate rotations for thigh box
            self.thigh.rotate(angle=radians(hip_rotate), axis=(0,1,0), origin=self.center_sphere.pos)
            thigh_axis = (-sin(radians(hip_set)),0,cos(radians(hip_set)))
            self.thigh.rotate(angle=radians(knee_rotate), axis=thigh_axis, origin=self.center_sphere.pos)

            #caluclate rotations for knee_sphere
            self.knee_sphere.rotate(angle=radians(hip_rotate), axis=(0,1,0), origin=self.center_sphere.pos)
            knee_sphere_axis = (-sin(radians(hip_set)),0,cos(radians(hip_set)))
            self.knee_sphere.rotate(angle=radians(knee_rotate), axis=knee_sphere_axis, origin=self.center_sphere.pos)

            #re-apply the distance between knee_sphere and foot_sphere relative to knee_sphere
            self.calf.pos = self.knee_sphere.pos-knee_calf_diff
            self.foot_sphere.pos = self.knee_sphere.pos-knee_foot_diff

            #caluclate rotations for thigh box
            self.calf.rotate(angle=radians(hip_rotate), axis=(0,1,0), origin=self.knee_sphere.pos)
            calf_axis = (-sin(radians(hip_set)),0,cos(radians(hip_set)))
            self.calf.rotate(angle=radians(knee_rotate+ankle_rotate), axis=calf_axis, origin=self.knee_sphere.pos)

            #rotate foot_sphere to keep it in line with knee_sphere
            self.foot_sphere.rotate(angle=radians(hip_rotate), axis=(0,1,0), origin=self.knee_sphere.pos)
            foot_sphere_axis = (-sin(radians(hip_set)),0,cos(radians(hip_set)))
            self.foot_sphere.rotate(angle=radians(knee_rotate+ankle_rotate), axis=foot_sphere_axis, origin=self.knee_sphere.pos)

    def hipSet(self, degrees=None, uS=None):
        #change the position angle of the hip
        if degrees:
            self.hipLock.acquire()
            self.hip_set = degrees
            self.hipLock.release()
        if uS:
            self.hipLock.acquire()
            self.hip_set = (uS-1500)/11.1111111111
            self.hipLock.release()

    def kneeSet(self, degrees=None, uS=None):
        #change the position angle of the hip

        if degrees:
            self.kneeLock.acquire()
            self.knee_set = degrees
            self.kneeLock.release()
        if uS:
            self.kneeLock.acquire()
            self.knee_set = (uS-1500)/11.1111111111
            self.kneeLock.release()

    def ankleSet(self, degrees=None, uS=None):
        #change the position angle of the hip
        if degrees:
            self.ankleLock.acquire()
            self.ankle_set = degrees
            self.ankleLock.release()
        if uS:
            self.ankleLock.acquire()
            self.ankle_set = (uS-1500)/11.1111111111
            self.ankleLock.release()


if __name__ == '__main__':
    RF = leg(origin=(-1,3,3))
    RM = leg(origin=(0,3,0))
    RB = leg(origin=(-1,3,-3))

    add=1.0
    deg=0.0
    while True:
        RF.hipSet(degrees=deg)
        RM.hipSet(degrees=-deg)
        RB.hipSet(degrees=deg)
        deg+=add
        if deg>30:
            add=-1
        if deg<-30:
            add=1
        time.sleep(0.03)

