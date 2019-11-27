class Pin:
    def __init__(self, pinNumber):
        self.pinNumber = pinNumber

    def __str__(self):
        return "This is Pin {}".format(self.pinNumber)
    
    def toDict(self):
        return {
            "pinNumber" : self.pinNumber
        }