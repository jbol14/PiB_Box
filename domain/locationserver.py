import socket
import os
import json
from locationcontroller import LocationController

## Konstanten
SOCKETPATH = "/tmp/unix.sock"
locationController = LocationController()

if os.path.exists(SOCKETPATH):
    os.remove(SOCKETPATH)

print("Opening Socket . . . ")

server = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)

server.bind(SOCKETPATH)

print("Listening on Socket")

while True:
    server.listen(20)
    conn, addr = server.accept()

    data = conn.recv(4096)

    if not data:
        break

    else:
        print("-"*20)

        dataString = data.decode("UTF-8")

        jsonData = json.loads(dataString)

        if jsonData["type"] == "ADD_RESERVATION":
            locationController.updateReservation(jsonData)
        
        elif jsonData["type"] == "ADD_SHARE":
            locationController.updateShare(jsonData)

        elif jsonData["type"] == "ADD_SERVICE":
            print(jsonData["payload"]) #Test
            locationController.updateService(jsonData)
        
        elif jsonData["type"] == "DELETE":
            locationController.deleteReservation(jsonData["id"])
        
        elif jsonData["type"] == "CHECK_RESERVATION":
            locationController.checkReservation(jsonData["key"])
        
        elif jsonData["type"] == "CHECK_SHARE":
            locationController.checkShare(jsonData["key"])
        
    
    conn.close()