import socket
import os
import json
import datetime
import time
#import RPi.GPIO as GPIO

## Konstanten
DATA = {}
SOCKETFILE = "/tmp/unix.sock"
LOGSOCK = "/tmp/firebase-logger.sock"
FILEPATH = "./data.json"

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(24, GPIO.OUT)

def used(user):
	payload = {"whoUsed" : user}
	
	return json.dumps(payload)


## TODO DATA persistieren, d.h. bei jedem Update DATA in Datei schreiben
## bei Startup DATA aus Datei lesen

## muss das wirkliche eine Funktion sein? Wird nur einmal am Anfang aufgerufen
def readFile(path):
	## falls Datei existiert: Inhalt auslesen und Inhalt in DATA speichern
	try:
		file = open(path, "rt")
		fileContent = json.loads(file.read())
	## Fall Datei nicht existiert, erstellen
	except FileNotFoundError:
		file = open(path, "x")
		fileContent = {}
	## Inhalt auslese und Datei schließen
	file.close()
	## Inhalt zurückgeben
	return fileContent

## Datei schreiben
def writeFile(path, data):
	try:
		file = open(FILEPATH,"w")
		file.write(data)
		file.close()
	except FileNotFoundError:
		print("Datei nicht gefunden")
	return 

DATA = readFile(FILEPATH)
print(DATA)

if os.path.exists(SOCKETFILE):
	os.remove(SOCKETFILE)

print("opening Socket ...")

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKETFILE)

print("Listening on Socket")

while True:
	## 20 zeitgleiche Verbindungen, da beim ersten aufrufen der Firebase App u.U. viele Reservierungen gesendet werden und das asynchron
	## Daher treffen mit großer Wahrscheinlichkeit neue Reservierungen ein, bevor bestehende Verbindungen geschlossen werden
	server.listen(20)
	conn, addr = server.accept()
	data = conn.recv(1024)
	if not data:
		break
	else:
		print("_"*20)
		dataString = data.decode("UTF-8")
		
		if "DONE" == dataString:
			break
		else:
			d = json.loads(dataString)
			## Empfangenes Objekt muss type-Feld haben
			## Mögliche Werte für type: 
			## ADD die empfangenen Daten sollen der Datenstruktur hinzugefügt werden
			## DELETE um eine Reservierung zu löschen
			## CHECK um zu prüfen, ob ein empfangener Schlüssel zu einer Reservierung gehört
			if d["type"] == "ADD":
				print("Updating reservation ", d["id"])
				## Aktualisiere DATA
				## D.h. füge ein neues Feld mit Schlüssel reservierungsId und Wert Payload zu Data hinzu
				DATA[d["id"]] = d["payload"]
				writeFile(FILEPATH, json.dumps(DATA))
				#print("Daten\n",DATA) #Test
			
			elif d["type"] == "DELETE":
				if d["id"] in DATA:
					print("Deleting reservation ", d["id"])
					del DATA[d["id"]]
					#print(DATA)
					writeFile(FILEPATH, json.dumps(DATA))
			
			elif d["type"] == "CHECK":
				## TODO : Übergebenen String parsen, userId extrahieren
				print("Checking Key")
				found = False
				key = d["key"]
				#print(key) # test
				# Box suchen, die mit dem empfangenen Schlüssel geöffnet werden kann
				for reservation in DATA:
					#print(DATA[reservation]) # test
					# Prüfen, ob Reservierung ein Key-Feld hat
					if "key" in DATA[reservation]: 
						#print(DATA[reservation])
						if DATA[reservation]["key"] == key:
							## Prüfen, ob die Reservierung jetzt gültig ist
							timeNow = datetime.datetime.now()
							# timeNow.timestamp() * 1000 um auf Nanosekunden zu kommen
							if timeNow.timestamp()*1000 >= DATA[reservation]["resFrom"] and timeNow.timestamp()*1000 <= DATA[reservation]["resTill"]:
								## falls Box gefunden wurde 
								## Setze "found"-Flag und sende die Box
								found = True
								print("Found matching reservation ", reservation)
								
								reply = json.dumps(DATA[reservation]) #Test
								#print("Box Data: ", reply) #Test
							
								## TODO Öffnen der Box hier implementieren
								## Dazu den Code aus Barcode-Scanner verwenden
								# GPIO.output(24, GPIO.HIGH)
								# sleep(0.2)
								# GPIO.output(24, GPIO.low)


								## Prüfen ob Counter-Feld existiert
								if "counter" in DATA[reservation]:
									DATA[reservation]["counter"] = DATA[reservation]["counter"] + 1
								else:
									DATA[reservation]["counter"] = 1

								## Firebase updaten
								if os.path.exists(LOGSOCK):
									client = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
									client.connect(LOGSOCK)
									print(type(DATA[reservation]))
									payload = '{"reservationId" : "' + reservation +'", "used" : ' + used("Ich") + '}'
									print("sending reply ", payload)
									client.send(payload.encode("UTF-8"))
									client.close()

							break
				# Kann weg wenn server auch boxen öffnet
				if not found:
					## Falls keine Box gefunden wurde
					## Sende leeres Objekt
					#conn.send(json.dumps({}).encode("UTF-8"))
					print("Keine passende Reservierung")
	
	## Verbindung wieder schließen
	conn.close()