import time
 
deg = 40

#set neck to where body is turning
hexy.neck.set(deg)

#re-plant tripod2 deg degrees forward
for leg in hexy.tripod2:
    leg.replantFoot(deg,stepTime=0.2)
time.sleep(0.3)

#raise tripod1 feet
for leg in hexy.tripod1:
    leg.setFootY(int(floor/2.0))
time.sleep(0.3)

#swing tripod2 feet back 2*deg degrees (to -deg)
for leg in hexy.tripod2:
    leg.setHipDeg(-deg,stepTime=0.3)

#reset neck as body turns
hexy.neck.set(0)
time.sleep(0.4)

#lower tripod1 feet
for leg in hexy.tripod1:
    leg.setFootY(floor)
time.sleep(0.3)

#re-plant legs to starting position
hexy.LF.replantFoot(deg,stepTime=0.3)
hexy.RM.replantFoot(1,stepTime=0.3)
hexy.LB.replantFoot(-deg,stepTime=0.3)

time.sleep(0.5)

