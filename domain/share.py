import os
import socket
import json

class Share:
    ## Globale Variablen
    LOGSOCKETPATH = "/tmp/firebase-logger.sock"

    ## Konstruktor
    def __init__(self, id, shareJson, reservation):
        #shareDict = json.loads(shareJson)
        print(shareJson)
        self.id = id
        self.fromUser = shareJson["fromUser"]
        self.toUser = shareJson["toUser"]
        self.qrCode = shareJson["qrCode"]
        self.reservationID = shareJson["reservationID"]
        self.reservation = reservation
    
    def logUsage(self):
        if os.path.exists(self.LOGSOCKETPATH):
            used = {"whoUsed" : self.toUser}
            payload = json.dumps({"reservationId" : self.reservationID, "used" : used })

            print(payload)

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.LOGSOCKETPATH)
            client.send(payload.encode("UTF-8"))
            client.close()
    
    def useShare(self):
        self.reservation.service.open()
        self.logUsage()
