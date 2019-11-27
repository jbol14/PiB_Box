import os
import datetime
import json
from service import Service
from reservation import Reservation
from share import Share

class LocationController:
    ## Globale Variablen
    RESERVATIONPATH = "./reservation.json"
    SHAREPATH = "./shares.json"
    SERVICEPATH = "./services.json"
    services = {}
    reservations = {}
    shares = {}
    
    ## Konstruktor
    def __init__(self):
        print("Initializing Location")

        # Services initialisieren
        servicesDict = self.readJsonFile(self.SERVICEPATH)
        for service in servicesDict:
            self.services[service] = Service(service, servicesDict[service]["category"],servicesDict[service]["gpioPin"])
        
        # Reservierungen initialisieren‚
        if not self.services == {}:
            reservationDict = self.readJsonFile(self.RESERVATIONPATH)
            for reservation in reservationDict:
                self.reservations[reservation] = Reservation(reservation, reservationDict[reservation], self.services[reservationDict[reservation]["serviceID"]])
        
        # Shares initialisieren
        if not self.reservations == {}:
            sharesDict = self.readJsonFile(self.SHAREPATH)
            for share in sharesDict:
                self.shares[share] = Share(share, sharesDict[share], self.reservations[sharesDict[share]["reservationID"]])


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
    
    ## Updating
    ## Resevierung
    def updateReservation(self, reservation):
        self.reservations[reservation["id"]] = Reservation(reservation["id"], reservation["payload"], self.services[reservation["payload"]["serviceID"]])
        self.writeJsonFile(self.RESERVATIONPATH, json.dumps(self.createJsonFromDict(self.reservations)))
    
    ## Share
    def updateShare(self, share):
        self.shares[share["id"]] = Share(share["id"], share["payload"], self.reservations[share["payload"]["reservationID"]])
        self.writeJsonFile(self.SHAREPATH, json.dumps(self.createJsonFromDict(self.shares)))
    
    ## Service
    def updateService(self, service):
        self.services[service["id"]] = Service(service["id"], service["payload"]["category"])
        self.writeJsonFile(self.SERVICEPATH, json.dumps(self.createJsonFromDict(self.services)))

    ## Löschen
    def deleteReservation(self, reservationID):
        ## Shares löschen, die zu dieser Reservierung gehören
        idsOfSharesToDelete = []
        for share in self.shares:
            if self.shares[share].reservationID == reservationID:
                idsOfSharesToDelete.append(share)
        for id in idsOfSharesToDelete:
            del self.shares[id]
        self.writeJsonFile(self.SHAREPATH, json.dumps(self.createJsonFromDict(self.shares)))
        try:
            del self.reservations[reservationID]
            self.writeJsonFile(self.RESERVATIONPATH, json.dumps(self.createJsonFromDict(self.reservations)))
        except KeyError:
            print("Keine Reservierung mit dieser ID")

    def deleteShare(self, shareID):
        try:
            del self.shares[shareID]
            self.writeJsonFile(self.SHAREPATH, json.dumps(self.createJsonFromDict(self.shares)))
        except KeyError:
            print("Keine Freigabe mit dieser ID")
    
    def deleteService(self, serviceID):
        try:
            reservations = []
            for reservation in self.reservations:
                if self.reservations[reservation].service.id == serviceID:
                    reservations.append(reservation["id"])
            
            for reservationID in reservations:
                self.deleteReservation(reservationID)

            
            del self.services[serviceID]

            self.writeJsonFile(self.SERVICEPATH, json.dumps(self.createJsonFromDict(self.services)))


        
        except KeyError:
            print("Key Error!")

    ## Checking
    def checkQrCode(self, key):
        ## Prüfen, ob Reservierung oder Freigabe getestet werden soll
        if key.split("=>")[3] == "false":
            self.checkReservation(key)
        else:
            self.checkShare(key)
    ## Interne Helfer
    def checkReservation(self, key):
        foundReservation = False
        for reservation in self.reservations:
            if self.reservations[reservation].qrCode == key:
                timeNow = datetime.datetime.now().timestamp() * 1000
                if timeNow >= self.reservations[reservation].resFrom and timeNow <= self.reservations[reservation].resTill:
                    foundReservation = True
                    self.reservations[reservation].useReservation()
        return foundReservation
    
    ##Subject to Change
    def checkShare(self, key):
        foundShare = False
        for share in self.shares:
            if self.shares[share].qrCode == key:
                timeNow = datetime.datetime.now().timestamp() * 1000
                if timeNow >= self.reservations[self.shares[share].reservationID].resFrom and timeNow <= self.reservations[self.shares[share].reservationID].resTill:
                    self.shares[share].useShare()
                    foundShare = True
        return foundShare


    def createJsonFromDict(self, dictionary):
        placeholder = {}
        for element in dictionary:
            placeholder[element] = dictionary[element].toDict()
        return placeholder