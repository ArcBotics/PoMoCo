import time

# Move: Lean Back

# Pick up back feet
hexy.RB.setHipDeg(-45,stepTime=0.3)
hexy.LB.setHipDeg(45,stepTime=0.3)
hexy.RB.setFootY(floor-40)
hexy.LB.setFootY(floor-40)

time.sleep(0.5)

# Push side feet down
hexy.RM.setFootY(floor+10)
hexy.RM.hip(70)
hexy.LM.setFootY(floor+10)
hexy.LM.hip(-70)
time.sleep(0.2)

# Put hands into air
hexy.LF.hip(-45)
hexy.LF.knee(0)
hexy.LF.ankle(0)
hexy.RF.hip(45)
hexy.RF.knee(0)
hexy.RF.ankle(0)
time.sleep(0.4)