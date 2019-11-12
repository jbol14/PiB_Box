#import RPi.GPIO as GPIO
#import time
import json

class Service:
    def __init__(self,id,category, gpioPin):
        ## GPIO Setup
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(gpioPin, GPIO.OUT)

        self.id = id
        self.category = category
        self.gpioPin = gpioPin
    
    def open(self):
        print("Opened Service {} at Pin {}".format(self.id, self.gpioPin))
        #GPIO.output(self.gpioPin, GPIO.HIGH)
        #sleep(0.2)
        #GPIO.output(self.gpioPin, GPIO.LOW)
    
    def getId(self):
        return self.id

    def getGpioPin(self):
        return self.gpioPin
    
    def toDict(self):
        return {
            "id" : self.id,
            "category" : self.category,
            "gpioPin" : self.gpioPin
            }
    
    def toJson(self):
        return json.dumps(self.toDict())
