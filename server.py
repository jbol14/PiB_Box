import socket
import os
import json
import datetime

## Konstanten
DATA = {}
SOCKETFILE = "/tmp/unix.sock"
FILEPATH = "./data.json"

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
				print("Updating")
				## Aktualisiere DATA
				## D.h. füge ein neues Feld mit Schlüssel reservierungsId und Wert Payload zu Data hinzu
				DATA[d["id"]] = d["payload"]
				writeFile(FILEPATH, json.dumps(DATA))
				print("Daten\n",DATA) #Test
			
			elif d["type"] == "DELETE":
				if d["id"] in DATA:
					print("Deleting")
					del DATA[d["id"]]
					print(DATA)
					writeFile(FILEPATH, json.dumps(DATA))
			
			elif d["type"] == "CHECK":
				print("Checking Key")
				found = False
				key = d["key"]
				print(key)
				# Box suchen, die mit dem empfangenen Schlüssel geöffnet werden kann
				for reservation in DATA:
					print(DATA[reservation])
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
								print("Found matching eservation")
								reply = json.dumps(DATA[reservation])
								print("Box Data: ", reply)
							#conn.send(reply.encode("UTF-8"))wird nicht gebraucht, Server soll Boxen öffnen
							## TODO Öffnen der Box hier implementieren
							## Dazu den Code aus Barcode-Scanner verwenden
							break
				# Kann weg wenn server auch boxen öffnet
				if not found:
					## Falls keine Box gefunden wurde
					## Sende leeres Objekt
					#conn.send(json.dumps({}).encode("UTF-8"))
					print("Keine passende Reservierung")
	
	## Verbindung wieder schließen
	conn.close()

# 1572362919.782624
# 1573977600000
# 1572247800000