import time

# Move: Typing

move('Lean Back')
time.sleep(0.3)

for i in range(10):
    hexy.RF.knee(0)
    hexy.LF.knee(60)

    time.sleep(0.3)

    hexy.RF.knee(60)
    hexy.LF.knee(0)

    time.sleep(0.3)
