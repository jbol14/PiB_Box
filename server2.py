import socket
import os
import json
from reservationcontroller import ReservationController

## Konstanten
SOCKETPATH  = "/tmp/unix.sock"
reservationController = ReservationController()


if os.path.exists(SOCKETPATH):
    os.remove(SOCKETPATH)

print("Opening Socket...")

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKETPATH)

print("Listening on Socket")

while True:
    server.listen(20)
    conn, addr = server.accept()

    data = conn.recv(1024)

    if not data:
        break

    else:
        print("_"*20)

        dataString = data.decode("UTF-8")

        jsonData = json.loads(dataString)

        if jsonData["type"] == "ADD":
            reservationController.updateReservations(jsonData)
        
        elif jsonData["type"] == "DELETE":
            reservationController.deleteReservation(jsonData["id"])
        
        elif jsonData["type"] == "CHECK":
            result = reservationController.checkReservation(jsonData["key"])
            if result:
                reservationController.openBox("TestID")
            else:
                print("No fitting Box")
    
    conn.close()
