from service import Service
import os
import socket
import json
import datetime

class Reservation:
    ## Globale Variablen
    LOGSOCKETPATH = "/tmp/firebase-logger.sock"
    PENDING_LOG_BUFFER_PATH = "./pending_logs.json"

    ## Konstruktor
    def __init__(self, id, reservationJson, service):
        #print(reservationJson["serviceID"]) # Test
        self.id = id
        self.serviceID = reservationJson["serviceID"] # Nicht sicher ob das gebraucht wird wenn Service als Attribut da ist
        self.resFrom = reservationJson["resFrom"]
        self.resTill = reservationJson["resTill"]
        #self.resTime = reservationJson["resTime"] # Nicht nötig
        self.userID = reservationJson["userID"]
        self.service = service
        self.userHasDeleted = reservationJson["userHasDeleted"]
        self.companyHasDeleted = reservationJson["companyHasDeleted"]
        #self.reasonWhyDeleted = reservationJsonreason["WhyDeleted"]
        #self.used = reservationJson["used"] # Nicht nötig
        self.qrCode = reservationJson["qrCode"]
    
    ## Methoden
    def logUsage(self):
        if os.path.exists(self.LOGSOCKETPATH):

            used = {"whoUsed" : self.userID}
            payload = {"reservationId" : self.id, "used" : used}

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                client.connect(self.LOGSOCKETPATH)
                client.send(json.dumps(payload).encode("UTF-8"))
                
            except ConnectionRefusedError:
                print("FirebaseUsage Logger not available")
                try:
                    payload["used"]["whenUsed"] = datetime.datetime.now().timestamp()
                    file = open(self.PENDING_LOG_BUFFER_PATH, "rt")
                    fileContent = json.loads(file.read())
                    file.close()
                    fileContent.append(payload)

                except FileNotFoundError:
                    fileContent = []
                    fileContent.append(payload)
                    
                finally:
                    file = open(self.PENDING_LOG_BUFFER_PATH, "w")
                    file.write(json.dumps(fileContent))
                    file.close()
            finally:
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
            #"used" : self.used,
            "qrCode" : self.qrCode
        }
    
    def toJson(self):
        return json.dumps(self.toDict())