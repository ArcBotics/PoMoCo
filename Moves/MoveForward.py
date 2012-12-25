import time

# Move: Move Forward

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
    hexy.LF.replantFoot(deg-hipSwing,stepTime=0.5)
    hexy.RM.replantFoot(hipSwing,stepTime=0.5)
    hexy.LB.replantFoot(-deg-hipSwing,stepTime=0.5)

    #   tripod1 moves behind
    hexy.RF.setHipDeg(-deg-hipSwing,stepTime=0.5)
    hexy.LM.setHipDeg(hipSwing,stepTime=0.5)
    hexy.RB.setHipDeg(deg-hipSwing,stepTime=0.5)
    time.sleep(0.6)

    # replant tripod1 forward while tripod2 move behind
    #   replant tripod1 forward
    hexy.RF.replantFoot(-deg+hipSwing,stepTime=0.5)
    hexy.LM.replantFoot(-hipSwing,stepTime=0.5)
    hexy.RB.replantFoot(deg+hipSwing,stepTime=0.5)

    #   tripod2 moves behind
    hexy.LF.setHipDeg(deg+hipSwing,stepTime=0.5)
    hexy.RM.setHipDeg(-hipSwing,stepTime=0.5)
    hexy.LB.setHipDeg(-deg+hipSwing,stepTime=0.5)
    time.sleep(0.6)
