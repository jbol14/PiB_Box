import socket
import os
import json
import datetime
import time
#import RPi.GPIO as GPIO

class ReservationController:

    ## Konstanten
    LOGSOCKETPATH = "/tmp/firebase-logger.sock"
    RESERVATIONPATH = "./reservation.json"
    SHAREPATH = "./shares.json"

    ## globale Variablen
    reservations = {}

    shares = {}

    ## Helfermethoden
    ''' Liest gegebene JSON-Datei und gibt Inhalt als Dictionary zurück '''
    def readJsonFile(self, path):
        try:
            file = open(path, "rt")
            fileContent = json.loads(file.read())
        except FileNotFoundError:
            file = open(path, "x")
            fileContent = {}
        
        return fileContent

    ''' Schreibt gegebenes Dictionary data in eine unter path spezifizierte Datei '''
    def writeJsonFile(self, path, data):
        try:
            file = open(path,"w")
            file.write(data)
            file.close()
        except FileNotFoundError:
            print("Invalid Path")

    ## Konstruktor
    def __init__(self):
        ## GPIO
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(24, GPIO.OUT)

        self.reservations = self.readJsonFile(self.RESERVATIONPATH)
        self.shares = self.readJsonFile(self.SHAREPATH)
    
    def openBox(self, reservationId):
        #GPIO.output(24, GPIO.HIGH)
        #sleep(0.2)
        #GPIO.output(24, GPIO.LOW)
        print("Box Opened")

    ## Updating
    def updateReservations(self, reservation):
        #print("Updating Reservation", reservation) ## Test
        self.reservations[reservation["id"]] = reservation["payload"]
        self.writeJsonFile(self.RESERVATIONPATH, json.dumps(self.reservations))
    
    def updateShares(self, share):
        print("Updating Share") ## Test
        self.shares[share["id"]] = share["payload"]
        self.writeJsonFile(self.SHAREPATH, json.dumps(self.shares))


    ## Deleting
    def deleteReservation(self, reservationId):
        print("Delete Reservation ", reservationId)
        ## Reservierung aus self.reservations entfernen
        if reservationId in self.reservations:
            del self.reservations[reservationId]
            self.writeJsonFile(self.RESERVATIONPATH, json.dumps(self.reservations))
        ## Freigaben für diese Reservierung Löschen
        listOfShareIds = []        
        for share in self.shares:
            if self.shares[share]["reservationID"] == reservationId:
                listOfShareIds.append(share)
                #del self.shares[share]
        
        print(listOfShareIds)
        
        for ids in listOfShareIds:
            print(ids, self.shares[ids])
            del self.shares[ids]

        self.writeJsonFile(self.SHAREPATH, json.dumps(self.shares))

    def deleteShare(self, shareId):
        if shareId in self.shares:
            del self.shares[shareId]
    

    ## Log Usage
    def logUsage(self, reservationId, user):
        if os.path.exists(self.LOGSOCKETPATH):
            client = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            client.connect(self.LOGSOCKETPATH)
            used = {"whoUsed" : user}
            payload = json.dumps({"reservationId" : reservationId, "used" : used})
            client.send(payload.encode("UTF-8"))
            client.close()


    
    ## Checking
    def checkReservation(self, key):
        foundReservation = False
        for reservation in self.reservations:
            if "key" in self.reservations[reservation]:
                if self.reservations[reservation]["key"] == key:
                    timeNow = datetime.datetime.now().timestamp() * 1000
                    if timeNow >= self.reservations[reservation]["resFrom"] and timeNow <= self.reservations[reservation]["resTill"]:
                        foundReservation = True
                        print("Found Matching Reservation")
                        print("Opening Box")
                        self.logUsage(reservation, "Ich")
                    break
        if foundReservation:
            return True
        else:
            return False

    
    ## TODO: Check shares

