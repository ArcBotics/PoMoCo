import time
 
deg = -30

# pickup and put all the feet centered and on the floor.

hexy.LF.replantFoot(-deg,stepTime=0.3)
hexy.RM.replantFoot(1,stepTime=0.3)
hexy.LB.replantFoot(deg,stepTime=0.3)

time.sleep(0.5)

hexy.RF.replantFoot(deg,stepTime=0.3)
hexy.LM.replantFoot(1,stepTime=0.3)
hexy.RB.replantFoot(-deg,stepTime=0.3)

time.sleep(0.5)

# set all the hip angle to what they should be while standing
hexy.LF.hip(-deg)
hexy.RM.hip(1)
hexy.LB.hip(deg)
hexy.RF.hip(deg)
hexy.LM.hip(1)
hexy.RB.hip(-deg)