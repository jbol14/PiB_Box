from service import Service
import os
import socket
import json

class Reservation:
    ## Globale Variablen
    LOGSOCKETPATH = "/tmp/firebase-logger.sock"

    ## Konstruktor
    def __init__(self, id, reservationJson, service):
        #print(reservationJson["serviceID"]) # Test
        self.id = id
        self.serviceID = reservationJson["serviceID"] #Nicht sicher ob das gebraucht wird wenn Service als Attribut da ist
        self.resFrom = reservationJson["resFrom"]
        self.resTill = reservationJson["resTill"]
        #self.resTime = reservationJson["resTime"] # Nicht nötig
        self.userID = reservationJson["userID"]
        self.service = service
        self.userHasDeleted = reservationJson["userHasDeleted"]
        self.companyHasDeleted = reservationJson["companyHasDeleted"]
        #self.reasonWhyDeleted = reservationJsonreason["WhyDeleted"]
        self.used = reservationJson["used"] # Nicht nötig
        self.qrCode = reservationJson["qrCode"]
    
    ## Methoden
    def logUsage(self):
        if os.path.exists(self.LOGSOCKETPATH):

            used = {"whoUsed" : self.userID}
            payload = json.dumps({"reservationId" : self.id, "used" : used})

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.LOGSOCKETPATH)
            client.send(payload.encode("UTF-8"))
            client.close()



    def useReservation(self):
        self.service.open()
        self.logUsage()
    
    def toDict(self):
        return {
            "id" : self.id,
            "serviceID" : self.serviceID,
            "resFrom" : self.resFrom,
            "resTill" : self.resTill,
            #"resTime" : self.resTime,
            "userID" : self.userID,
            "userHasDeleted" : self.userHasDeleted,
            "companyHasDeleted" : self.companyHasDeleted,
            "used" : self.used,
            "qrCode" : self.qrCode
        }
    
    def toJson(self):
        return json.dumps(self.toDict())