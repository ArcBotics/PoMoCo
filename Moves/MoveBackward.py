import time

# Move: Move Backward

deg = 25
midFloor = 30
hipSwing = 25
pause = 0.5

# tripod1 = RF,LM,RB
# tripod2 = LF,RM,LB

for timeStop in range(2):
    # replant tripod2 backwards while tripod1 moves forward
    #   relpant tripod 2 backwards
    hexy.LF.replantFoot(deg+hipSwing,stepTime=0.5)
    hexy.RM.replantFoot(-hipSwing,stepTime=0.5)
    hexy.LB.replantFoot(-deg+hipSwing,stepTime=0.5)

    #   tripod1 moves forward
    hexy.RF.setHipDeg(-deg+hipSwing,stepTime=0.5)
    hexy.LM.setHipDeg(-hipSwing,stepTime=0.5)
    hexy.RB.setHipDeg(deg+hipSwing,stepTime=0.5)
    time.sleep(0.6)

    # replant tripod1 backwards while tripod2 moves behind
    #   replant tripod1 backwards
    hexy.RF.replantFoot(-deg-hipSwing,stepTime=0.5)
    hexy.LM.replantFoot(hipSwing,stepTime=0.5)
    hexy.RB.replantFoot(deg-hipSwing,stepTime=0.5)

    #   tripod2 moves behind
    hexy.LF.setHipDeg(deg-hipSwing,stepTime=0.5)
    hexy.RM.setHipDeg(hipSwing,stepTime=0.5)
    hexy.LB.setHipDeg(-deg-hipSwing,stepTime=0.5)
    time.sleep(0.6)

