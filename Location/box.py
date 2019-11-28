from pin import Pin
class Box:
    def __init__(self, boxNumber, pin):
        self.boxNumber = boxNumber
        self.pin = pin

    def __str__(self):
        return "This is Box No {}, using Pin {}".format(self.boxNumber, self.pin.pinNumber)

    def toDict(self):
        return{
            "boxNumber" : self.boxNumber,
            "pin" : self.pin.toDict()
        }