import os
import socket
import json
import datetime

class Share:
    ## Globale Variablen
    LOGSOCKETPATH = "/tmp/firebase-logger.sock"
    PENDING_LOG_BUFFER_PATH = "./Configuration/pending_logs.json"

    ## Konstruktor
    def __init__(self, id, shareJson, reservation):
        #shareDict = json.loads(shareJson)
        #print(shareJson)
        self.id = id
        self.fromUser = shareJson["fromUser"]
        self.toUser = shareJson["toUser"]
        self.qrCode = shareJson["qrCode"]
        self.reservationID = shareJson["reservationID"]
        self.reservation = reservation
    
    def logUsage(self):
        if os.path.exists(self.LOGSOCKETPATH):
            used = {"whoUsed" : self.toUser}
            payload = {"reservationId" : self.reservationID, "used" : used }
            
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
                    print("no file")
                    fileContent = []
                    fileContent.append(payload)
                    
                finally:
                    file = open(self.PENDING_LOG_BUFFER_PATH, "w")
                    file.write(json.dumps(fileContent))
                    file.close()    
            finally:
                client.close()

    
    def useShare(self):
        self.reservation.service.open()
        self.logUsage()

    def toDict(self):
        return {
            "id" : self.id,
            "qrCode" : self.qrCode,
            "toUser" : self.toUser,
            "fromUser" : self.fromUser,
            "reservationID" : self.reservationID
        }
    
    def toJson(self):
        return json.dumps(self.toDict())