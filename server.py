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
	server.listen(1)
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
			print(dataString)
			d = json.loads(dataString)
			if d["type"] == "UPDATE":
				print("Updating")
				DATA = d["BOXEN"]
			elif d["type"] == "CHECK":
				print("Checking Key")
				found = False
				key = d["key"]
				for box in DATA:
					if DATA[box]["key"] == key:
						found = True
						print("Found matching Box")
						reply = json.dumps(DATA[box])
						print("Box Data: ", reply)
						conn.send(reply.encode("UTF-8"))
						break
				if not found:
					conn.send(json.dumps({}).encode("UTF-8"))

