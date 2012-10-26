import time
import math
import serial
import serial.tools.list_ports
import threading
 
debug = False
startTime = time.clock()
serialSends = []

class runMovement(threading.Thread):

	def __init__(self,function,*args):
		threading.Thread.__init__(self)
		self.function=function
		self.args = args
		self.start()

	def run(self):
		self.function(*self.args)

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
		print "Ser Open Status:",self.serOpen
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
						else:
							time.sleep(0.01) # keeps infinite while loop from killing processor
						if send:
							#print str(time.clock())+","+str(toSend)
							sending = str(toSend)
							#print sending
							self.ser.write(sending)
							#sendTime = time.clock()-startTime
							#serialSends.append([float(sendTime),str(toSend)])
							time.sleep(0.005)
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
		"""
		ser = serial.Serial("/dev/tty.usbmodem1411", 115200, timeout=1)
		time.sleep(2)
		print "serial connected!"
		self.ser = ser
		
		self.ser.flush()
		time.sleep(1)
		self.ser.write("V\n")
		self.serOpen = True
		self.serNum = 1
		"""
		comList = []
		comports = serial.tools.list_ports.comports()
		for comport in comports:
			for thing in comport:
				comList.append(thing)
		
		comList = list(set(comList))
		print "Attempting to connect to Servotor"
		for port in comList:
			try:
				ser = serial.Serial(port, 115200, timeout=1)
				ser.write('V\n')
				result = ser.readline()
				if "SERVOTOR" in result:
					print "Connect Successful! Connected on port:",port
					self.ser = ser
					self.ser.flush()
					self.serOpen = True
					self.serNum = 1
					break
			except:
				pass

	


class Servo:

	def __init__(self,servoNum,serHandler,servoPos=1500,offset=0,active=False):
		self.serHandler = serHandler
		self.active = active
		self.servoNum = servoNum

		#servo position and offset is stored in microseconds (uS)
		self.servoPos = servoPos
		self.offset = offset

	def setPos(self,timing=None,deg=None,move=True):
		if timing != None:
			self.servoPos = timing
		if deg != None:
			self.servoPos = int(1500.0+float(deg)*11.1111111)
		if move:
			self.active = True
			self.move()
			if debug: print "moved ",self.servoNum
		if debug: print "servo",self.servoNum,"set to",self.servoPos

	def getPosDeg(self):
		return (self.servoPos-1500)/11.1111111

	def getPosuS(self):
		return self.servoPos

	def getActive(self):
		return self.active

	def getOffsetDeg(self):
		return (self.offset-1500)/11.1111111

	def getOffsetuS(self):
		return self.offset

	def setOffset(self,timing=None,deg=None):
		if timing != None:
			self.offset = timing
		if deg != None:
			self.offset = int(float(deg)*11.1111111)

	def reset(self):
		self.setPos(timing=1500)
		self.move()

	def kill(self):
		self.active = False
		toSend = "#%dL\r"%(self.servoNum)
		self.serHandler.sendLock.acquire()
		self.serHandler.sendQueue.append(toSend)
		self.serHandler.sendLock.release()
		if debug: print "sending command #%dL to queue"%self.servoNum

	def move(self):
		if self.active:
			if debug: print "sending command #%dP%d to queue"%(self.servoNum,int(self.servoPos)+int(self.offset))
			# send the message the serial handler in a thread-safe manner
			toSend = "#%dP%d\r"%(self.servoNum,int(self.servoPos)+int(self.offset))
			self.serHandler.sendLock.acquire()
			self.serHandler.sendQueue.append(toSend)
			self.serHandler.sendLock.release()
		else:
			try:
				toSend = "#%dL\r"%(self.servoNum,int(self.servoPos))
				self.serHandler.sendLock.acquire()
				self.serHandler.sendQueue.append(toSend)
				self.serHandler.sendLock.release()
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
			self.servos[i].kill()

		print "servos initalizied"

	def killAll(self):
		if self.serialHandler.serOpen:
			for servo in self.servos:
				self.servos[servo].kill()
		print "SHUTTING. DOWN. EVERYTHING. All servos killed."

if __name__ == '__main__':
	pass
	conn = Controller()
	#conn.servos[1].setPos(deg=30)

