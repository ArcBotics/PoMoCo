import time
import math
import serial
import threading
import hexSim

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

        while(True):
            #print "command cycle"

            #send waiting messages
            self.sendLock.acquire()
            if self.serOpen:
                if self.ser.writable:
                    if(len(self.sendQueue)>0):
                        toSend = self.sendQueue.pop(0)
                        if debug: print "sending '%s' to COM %d"%(str(toSend),self.serNum+1)
                        if self.serOpen:
                            self.ser.write(str(toSend))
            self.sendLock.release()


            #retreive waiting responses
            #don't need reading yet, holding off on fully implementing it till needed
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
        #auto attach to controller
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

class serMsgSend(threading.Thread):

    def __init__(self,serialHandler,msg):
        threading.Thread.__init__(self)
        self.serialHandler = serialHandler
        self.msg=msg
        self.start()

    def run(self):
        if debug: print "adding %s to queue for COM %d"%(str(self.msg),self.serialHandler.serNum+1)
        self.serialHandler.sendLock.acquire()
        self.serialHandler.sendQueue.append(self.msg)
        self.serialHandler.sendLock.release()

class Servo:

    def __init__(self,servoNum,serHandlerInstance,servoPos=1500):

        self.active = 0
        self.servoPos = servoPos
        self.servoNum = servoNum
        self.offset = 0
        self.serHandler = serHandlerInstance

    def setPos(self,timing=None,degrees=None,move=True):
        if timing != None:
            self.active = 1
            self.servoPos = timing
            self.move()
            if debug: print "moved ",self.servoNum
        if degrees != None:
            self.active = 1
            self.servoPos = int(1500+degrees*11.1111111)
            self.move()
            if debug: print "moved ",self.servoNum

    def getPosDeg(self):
        return (self.servoPos-1500)/11.1111111

    def setOffset(self,timing=1500,degrees=0.0):
        if timing != 1500:
            pass
        if degrees != 0.0:
            pass

    def offsetInc(self):
        self.offset += 10
        self.move()

    def offsetDec(self):
        self.offset -= 10
        self.move()

    def kill(self):
        self.active = 0
        self.move()

    def move(self):
        if self.active == 0:
            try:
                serMsg = serMsgSend(self.serHandler,"#%dL\r"%self.servoNum)
                if debug: print "sending command #%dL\r to queue"%self.servoNum
            except:
                pass
        else:
            if debug: print "sending command #%dP%dT0\r to queue"%(self.servoNum,int(self.servoPos))
            serMsg = serMsgSend(self.serHandler,"#%dP%dT0\r"%(self.servoNum,int(self.servoPos)))



    def reset(self):
        self.setPosition(timing=1500)
        self.move()


class Controller:
    def __init__(self,servos=32):
        self.serialHandler = serHandler()
        timeout = time.time()
        while not (self.serialHandler.serOpen or (time.time()-timeout > 2.0)):
            time.sleep(0.01)
        self.servos = {}
        for i in range(32):
            self.servos[i]=Servo(i,serHandlerInstance=self.serialHandler)

        print "initialized all 32 servos 0-31 to 1500uS"

    def killAll(self):
        if self.serialHandler.serOpen:
            for servo in self.servos:
                self.servos[servo].kill()

if __name__ == '__main__':
    conn = Controller()
    conn.servos[1].setPos(degrees=30)

