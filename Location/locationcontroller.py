import os
import datetime
import json
from service import Service
from reservation import Reservation
from share import Share
from box import Box
from pin import Pin

class LocationController:
    ## Globale Variablen
    RESERVATIONPATH = "./Configuration/reservation.json"
    SHAREPATH = "./Configuration/shares.json"
    SERVICEPATH = "./Configuration/services.json"
    AVAILABLEBOXESPATH = "./Configuration/boxes.json"
    services = {}
    reservations = {}
    shares = {}
    availableBoxes = []
    usedBoxes = []
    
    ## Konstruktor
    def __init__(self):
        
        print("Initializing Location")

        try:
        
            boxesDict = open(self.AVAILABLEBOXESPATH,"rt").read()
        
            self.availableBoxes = json.loads(boxesDict)["available"]
            self.usedBoxes = json.loads(boxesDict)["used"]
        
            print(self.availableBoxes)
        
        except FileNotFoundError:
        
            print("Bitte Setup ausführen")
            ## Beenden
            exit()


        # Services initialisieren
        servicesDict = self.readJsonFile(self.SERVICEPATH)
        
        for service in servicesDict:
        
            self.services[service] = Service(service, servicesDict[service]["category"],Box(servicesDict[service]["box"]["boxNumber"], Pin(servicesDict[service]["box"]["pin"]["pinNumber"])))
        
        # Reservierungen initialisieren‚ falls es Services gibt
        if not self.services == {}:
        
            reservationDict = self.readJsonFile(self.RESERVATIONPATH)
        
            for reservation in reservationDict:
        
                self.reservations[reservation] = Reservation(reservation, reservationDict[reservation], self.services[reservationDict[reservation]["serviceID"]])
        
        # Shares initialisieren, falls es Reservierungen gibt
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
        ## TODO
        ## Prüfen, ob der empfangene service bereits bekannt ist oder ob er wirklich neu ist
        ## Falls bekannt: Dann ist er in self.services
        serviceID = service["id"]

        if service["id"] in self.services:
            boxNumber = self.services[serviceID].box.boxNumber
            pinNumber = self.services[serviceID].box.pin.pinNumber
            self.services[serviceID] = Service(serviceID,service["payload"]["category"], Box(boxNumber,Pin(pinNumber)))
        else:
            box = self.availableBoxes.pop()

            concreteBox = Box(box["boxNumber"], Pin(box["pin"]["pinNumber"]))

            ## Wenn Service bekannt muss nur das hier ausgeführt werden, - concreteBox, die muss aus den Eigenschaften des Services hergestellt werden

            self.services[service["id"]] = Service(service["id"], service["payload"]["category"], concreteBox)

            self.usedBoxes.append(concreteBox.toDict())


        self.writeJsonFile(self.SERVICEPATH, json.dumps(self.createJsonFromDict(self.services)))

        #self.writeJsonFile(self.AVAILABLEBOXESPATH, json.dumps({"available" : self.availableBoxes, "used" : self.usedBoxes}))

        

        tempBx = []

        dc = {}

        for box in self.availableBoxes:
            print("available: Typ: ", type(box))
            tempBx.append(box)
        
        dc["available"] = tempBx

        tempBx = []

        for box in self.usedBoxes:
            print("Used: Typ: ", type(box))
            tempBx.append(box)
        
        dc["used"] = tempBx

        self.writeJsonFile(self.AVAILABLEBOXESPATH, json.dumps(dc))






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
    
                    reservations.append(reservation)
            
            for reservationID in reservations:
    
                self.deleteReservation(reservationID)

            ## Für Service verwendete Box wieder freigeben
            service = self.services[serviceID]
            #print(box.box.toDict())
            self.availableBoxes.append(self.services[serviceID].box.toDict())
            ## TODO: Aus verfügbaren Boxen entfernen
            counter = 0

            print(service.box.boxNumber)
            for box in self.usedBoxes:
                
                if box["boxNumber"] == service.box.boxNumber:
                    print(box)
                    break
                counter += 1
            
            throwAway = self.usedBoxes.pop(counter)

            print(throwAway, serviceID)

            
            del self.services[serviceID]

            tmpBx = []
            dc = {}
            for box in self.availableBoxes:
                tmpBx.append(box)
            dc["available"] = tmpBx

            tmpBx = []
            for box in self.usedBoxes:
                tmpBx.append(box)
            dc["used"] = tmpBx

            self.writeJsonFile(self.AVAILABLEBOXESPATH, json.dumps(dc))

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