import time
import math
import serial
import threading

debug = False

class serHandler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.ser = None

        self.sendQueue=[]
        self.sendLock = threading.Lock()

        self.recieveQueue=[]
        self.recieveLock = threading.Lock()

        self.serOpen = False
        self.serNum = 0

        self.start()

    def run(self):
        self.connect()
        if self.serOpen:
            if self.ser.writable:
                if self.serOpen:

                    while(True):
                    # send waiting messages
                        send = False
                        if(len(self.sendQueue)>0):
                            self.sendLock.acquire()
                            toSend = self.sendQueue.pop(0)
                            self.sendLock.release()
                            send = True
                        if send: self.ser.write(str(toSend))
                        if debug:
                            print "sent '%s' to COM%d"%(str(toSend).strip('\r'),self.serNum+1)

            # retreive waiting responses
            #  don't need reading yet, holding off on fully implementing it till needed
            """
            if self.ser.readable():
                read = self.ser.read()
                if len(read) == 0:
                    pass
                    #print "derp"
                else:
                    if debug: print "recieved %s from COM %d"%(str(read),self.serNum+1)
                    self.recieveLock.acquire()
                    self.recieveQueue.append(read)
                    self.recieveLock.release()
            """

    def connect(self):
        # auto attach to controller
        self.serOpen = False
        for i in range(1,100):
            try:
                try:
                    ser = serial.Serial(i, baudrate=115200, timeout=1)
                except:
                    raise Exception
                ser.flush()
                time.sleep(0.1)
                ser.write("VER\r")
                time.sleep(0.1)
                readReply = ser.read(5)
                if readReply == 'SSC32':
                    print "controller found at port:",i+1
                    ser.flush()
                    self.ser = ser
                    print "connected to port",i+1
                    self.serNum = i
                    self.serOpen = True
                    break
                else:
                    ser.close()
                    pass
            except:
                pass
        if self.serOpen == False:
            print "no serial ports available, just showing graphical"

class Servo:

    def __init__(self,servoNum,serHandler,servoPos=1500,offset=0,active=True):
        self.serHandler = serHandler
        self.active = active
        self.servoNum = servoNum

        #servo position and offset is stored in microseconds (uS)
        self.servoPos = servoPos
        self.offset = offset


    def setPos(self,timing="None",degrees="None",move=True):

        if timing != "None":
            self.servoPos = timing
        if degrees != "None":
            self.servoPos = int(1500.0+float(degrees)*11.1111111)
        if move:
            self.active = True
            self.move()
            if debug: print "moved ",self.servoNum
        if debug: print "servo",self.servoNum,"set to",self.servoPos

    def getPosDeg(self):
        return (self.servoPos-1500)/11.1111111

    def getPosuS(self):
        return self.servoPos

    def getOffsetDeg(self):
        return (self.offset-1500)/11.1111111

    def getOffsetuS(self):
        return self.offset

    def setOffset(self,timing=1500,degrees=0.0):
        if timing != 1500:
            pass
        if degrees != 0.0:
            pass

    def reset(self):
        self.setPos(timing=1500)
        self.active = False
        self.move()

    def kill(self):
        self.active = False
        self.move()

    def move(self):
        if self.active:
            if debug: print "sending command #%dP%dT0 to queue"%(self.servoNum,int(self.servoPos))
            # send the message the serial handler in a thread-safe manner
            toSend = "#%dP%dT0\r"%(self.servoNum,int(self.servoPos))
            self.serHandler.sendLock.acquire()
            self.serHandler.sendQueue.append(toSend)
            self.serHandler.sendLock.release()
        else:
            try:
                serMsg = serMsgSend(self.serHandler,"#%dL\r"%self.servoNum)
                if debug: print "sending command #%dL to queue"%self.servoNum
            except:
                pass

class Controller:
    def __init__(self,servos=32):
        self.serialHandler = serHandler()
        timeout = time.time()
        while not (self.serialHandler.serOpen or (time.time()-timeout > 2.0)):
            time.sleep(0.01)
        print "initilizing servos"
        self.servos = {}
        for i in range(32):
            self.servos[i]=Servo(i,serHandler=self.serialHandler)
        print "servos initalizied"

    def killAll(self):
        if self.serialHandler.serOpen:
            for servo in self.servos:
                self.servos[servo].kill()
        print "SHUTTING. DOWN. EVERYTHING. All servos killed."

if __name__ == '__main__':
    pass
    #conn = Controller()
    #conn.servos[1].setPos(degrees=30)

