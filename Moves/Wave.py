import time

# Move: Wave
hexy.neck.set(0)

hexy.LF.hip(-20)
hexy.LF.knee(0)
hexy.LF.ankle(0)

time.sleep(0.2)

for i in range(3):
    hexy.LF.hip(-20)
    hexy.LF.knee(-50)
    hexy.LF.ankle(-20)

    time.sleep(0.2)

    hexy.LF.knee(-10)
    hexy.LF.ankle(0)
    time.sleep(0.2)

hexy.LF.knee(-40)