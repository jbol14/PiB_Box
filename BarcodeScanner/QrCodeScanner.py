import cv2
from pyzbar import pyzbar
import imutils
from imutils.video import VideoStream
import time
import socket
import os
import json

SOCKETFILE = "/tmp/unix.sock"

vs = VideoStream(usePiCamera = True).start()
time.sleep(2.0)

while True:
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	barcodes = pyzbar.decode(frame)
	#Finally there should always be a single QR-Code
	for barcode in barcodes:
		print(barcode.data.decode("utf-8"))
		key = barcode.data.decode("UTF-8")
		
		if os.path.exists(SOCKETFILE):
			client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			try:
				client.connect(SOCKETFILE)

				keyFields = key.split("=>")

				if len(keyFields) is not 5:
					break

				if keyFields[3] == "false":
					operationType = "CHECK_RESERVATION"
			
				else:
					operationType = "CHECK_SHARE"
				
				print("Connected to Socket")

				req = {
				"type" : operationType,
				"key" : key
				}
						
				client.send(json.dumps(req).encode("UTF-8"))
			except ConnectionRefusedError:
				print("Tried to scan QR-Code, but LoactionServer was not available")
			finally:
				client.close()
				time.sleep(3.0)