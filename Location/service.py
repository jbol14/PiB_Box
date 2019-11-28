#import RPi.GPIO as GPIO
import time
import json

class Service:
    def __init__(self,id,category, box):
        ## GPIO Setup
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(gpioPin, GPIO.OUT)

        self.id = id
        self.category = category
        self.box = box
    
    def open(self):
        print("Opened Service {} at Pin {}".format(self.id, self.getGpioPin()))
        # GPIO.output(self.gpioPin, GPIO.HIGH)
        # time.sleep(0.2)
        # GPIO.output(self.gpioPin, GPIO.LOW)
    
    def getId(self):
        return self.id

    def getGpioPin(self):
        return self.box.pin.pinNumber
    
    def toDict(self):
        print("Box: ", type(self.box))
        return {
            "id" : self.id,
            "category" : self.category,
            "box" : self.box.toDict()
        }
    
    def toJson(self):
        return json.dumps(self.toDict())
