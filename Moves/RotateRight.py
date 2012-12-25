import time

deg = -40

# set neck to where body is turning
hexy.neck.set(deg)

# re-plant tripod1 deg degrees forward
for leg in hexy.tripod1:
    leg.replantFoot(deg,stepTime=0.2)
time.sleep(0.5)

# raise tripod2 feet in place as tripod1 rotate and neck
for leg in hexy.tripod2:
    leg.setFootY(int(floor/2.0))
time.sleep(0.3)

# swing tripod1 feet back 2*deg degrees (to -deg)
for leg in hexy.tripod1:
    leg.setHipDeg(-deg,stepTime=0.3)

# reset neck as body turns
hexy.neck.set(0)
time.sleep(0.4)

# lower tripod2 feet
for leg in hexy.tripod2:
    leg.setFootY(floor)
time.sleep(0.3)

# re-plant legsto starting position
hexy.RF.replantFoot(deg,stepTime=0.3)
hexy.LM.replantFoot(1,stepTime=0.3)
hexy.RB.replantFoot(-deg,stepTime=0.3)

time.sleep(0.3)

