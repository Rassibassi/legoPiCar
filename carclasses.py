import socket
import threading
import RPi.GPIO as GPIO
import time

class CarPositionWrapper():
    def __init__(self):
        self.position = 0
        self.acceleration = 0

    def setPosition(self, position):
        self.position=int(position)

    def getPosition(self):
        return self.position

    def setAcceleration(self, acceleration):
        self.acceleration=int(acceleration)

    def getAcceleration(self):
        return self.acceleration

class CarControl(threading.Thread):
    def __init__(self,car,carpositionwrapper,lock):
        threading.Thread.__init__(self)
        self.car=car
        self.cpw=carpositionwrapper
        self.lock=lock

    def run(self):
        while True:
            self.lock.acquire()
            position = self.cpw.getPosition()
            acceleration = self.cpw.getAcceleration()
            self.lock.release()
            print position, " --- ", acceleration;
            self.car.move(acceleration)
            self.car.steer(position)

class CarListener(threading.Thread):
    def __init__(self,carpositionwrapper,lock):
        threading.Thread.__init__(self)
        self.cpw=carpositionwrapper
        self.lock = lock

    def run(self):
        UDP_IP = "192.168.0.12"
        UDP_PORT = 5005
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        while True:
            data, addr = sock.recvfrom(1024)
            position = data.split(";")[0]
            acceleration = data.split(";")[1]
            self.lock.acquire()
            self.cpw.setPosition(position)
            self.cpw.setAcceleration(acceleration)
            self.lock.release()
            print "received message:", data

class Car(object):
    def __init__(self):
        self.position = 0
        self.acceleration = 0

        self.pins = [8, 10, 16, 18]

        GPIO.setmode(GPIO.BOARD)
        for i in self.pins:
            GPIO.setup(i, GPIO.OUT)
            GPIO.output(i, False)

    def cleanup(self):
        GPIO.cleanup()

    def move(self,acceleration):
        if acceleration == 0:
            GPIO.output(self.pins[2], False)
            GPIO.output(self.pins[3], False)
        elif acceleration == 1:
            GPIO.output(self.pins[2], True)
            GPIO.output(self.pins[3], False)
        elif acceleration == 2:
            GPIO.output(self.pins[2], False)
            GPIO.output(self.pins[3], True)

    def steer(self,new_position):        
        if self.position > new_position:
            if self.position != -16:
                self.steer_left()
                self.position = self.position - 1
        elif self.position < new_position:
            if self.position != 16:
                self.steer_right()
                self.position = self.position + 1        

    def steer_left(self):
        GPIO.output(self.pins[0], True)
        GPIO.output(self.pins[1], False)
        time.sleep(0.025)
        GPIO.output(self.pins[0], False)

    def steer_right(self):
        GPIO.output(self.pins[0], False)
        GPIO.output(self.pins[1], True)
        time.sleep(0.025)
        GPIO.output(self.pins[1], False)