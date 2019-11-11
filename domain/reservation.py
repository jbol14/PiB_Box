from service import Service
import os
import socket
import json

class Reservation:
    ## Globale Variablen
    LOGSOCKETPATH = "/tmp/firebase-logger.sock"

    ## Konstruktor
    def __init__(self, id, reservationJson, service):
        print(reservationJson["serviceID"])
         #reservationDict = json.loads(reservationJson)
        self.id = id
        self.serviceID = reservationJson["serviceID"]
        self.resFrom = reservationJson["resFrom"]
        self.resTill = reservationJson["resTill"]
        #self.resTime = reservationJson["resTime"]
        self.userID = reservationJson["userID"]
        self.service = service
        self.userHasDeleted = reservationJson["userHasDeleted"]
        self.companyHasDeleted = reservationJson["companyHasDeleted"]
        #self.reasonWhyDeleted = reservationJsonreason["WhyDeleted"]
        self.used = reservationJson["used"]
        self.qrCode = reservationJson["key"]
    
    ## Methoden
    def logUsage(self):
        if os.path.exists(self.LOGSOCKETPATH):

            used = {"whoUsed" : self.userID}
            payload = json.dumps({"reservationId" : self.id, "used" : used})

            print(payload) ## Test

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.LOGSOCKETPATH)
            client.send(payload.encode("UTF-8"))
            client.close()



    def useReservation(self):
        self.service.open()
        self.logUsage()