import time
 
deg = -30

#put all the feet centered and on the floor.

hexy.LF.hip(-deg)
hexy.RM.hip(1)
hexy.LB.hip(deg)

hexy.RF.hip(deg)
hexy.LM.hip(1)
hexy.RB.hip(-deg)

time.sleep(0.5)

for leg in hexy.legs:
    leg.knee(-30)
    leg.hip("sleep")

time.sleep(0.5)

for leg in hexy.legs:
    leg.ankle(-90)

time.sleep(0.5)

for angle in range(0,45,3):
    for leg in hexy.legs:
        leg.knee(angle)
        leg.ankle(-90+angle)
    time.sleep(0.1)

move("Reset")