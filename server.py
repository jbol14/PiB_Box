import socket
import os
import json

DATA = {}

SOCKETFILE = "/tmp/unix.sock"

if os.path.exists(SOCKETFILE):
	os.remove(SOCKETFILE)

print("opening Socket ...")

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKETFILE)

print("Listening on Socket")

while True:
	## Allow 2 simultaneous Connections (Firebase App and Barcode Scanner)
	server.listen(2)
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
			#print(dataString)
			d = json.loads(dataString)
			## Provided Data must have a type field
			## Possible types: 
			## UPDATE to update the internal data
			## CHECK to check if a provided key belongs to a box
			if d["type"] == "ADD":
				print("Updating")
				## Aktualisiere DATA
				## D.h. füge ein neues Feld mit Schlüssel reservierungsId und Wert Payload zu Data hinzu
				DATA[d["id"]] = d["payload"]
				print("Daten\n",DATA) #Test
			elif d["type"] == "DELETE":
				if d["id"] in DATA:
					del DATA[d["id"]]
					print(DATA)
			elif d["type"] == "CHECK":
				print("Checking Key")
				found = False
				key = d["key"]
				## Search for the Box that can be opened with the provided Key
				for box in DATA:
					if DATA[box]["key"] == key:
						## If the propper Box was found, 
						## set found flag, send the Boxdata
						found = True
						print("Found matching Box")
						reply = json.dumps(DATA[box])
						print("Box Data: ", reply)
						conn.send(reply.encode("UTF-8"))
						break
				if not found:
					## If no Box was found
					## send an empty Dictionary
					conn.send(json.dumps({}).encode("UTF-8"))
			else:
				print("Mist")

