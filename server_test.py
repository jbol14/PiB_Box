import socket
import os
import json
import time



def buildJsonString(key, opType):
    dictionary = {
        "type" : opType
    }
    dictionary["key"] = key

    jsonString = json.dumps(dictionary)

    return jsonString

def sendKeyToServer(key, opType):
    SOCKETFILE = "/tmp/unix.sock"
    if os.path.exists(SOCKETFILE):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKETFILE)
        client.send(buildJsonString(key,opType).encode("UTF-8"))
    else:
        print("Socket nicht verfügbar")

testKeyReservation = "=>GSDnzEFodIpumQYVzKAP=>6BVUaRPRC1hYGRaMuhcp0XH24vj2=>false=>GLuM90ILYHonVJ2ZdVfk"
testKeyShare = "=>GSDnzEFodIpumQYVzKAP=>6BVUaRPRC1hYGRaMuhcp0XH24vj2=>soOTjIp2vSSt6mRf42zGYYNiTiV2=>GLuM90ILYHonVJ2ZdVfk"

# print(testKeyShare.split("=>"))
# if testKeyShare.split("=>")[3] == "false":
#     operation = "CHECK_RESERVATION"
# else:
#     operation = "CHECK_SHARE"



sendKeyToServer(testKeyReservation,"CHECK_QR_CODE")


time.sleep(5)

# if testKeyReservation.split("=>")[3] == "false":
#     operation = "CHECK_RESERVATION"
# else:
#     operation = "CHECK_SHARE"

sendKeyToServer(testKeyShare, "CHECK_QR_CODE")