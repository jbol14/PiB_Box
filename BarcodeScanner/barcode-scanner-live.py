import cv2
from pyzbar import pyzbar
import imutils
from imutils.video import VideoStream
import time
import socket
import os
import json

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
## Define Output Pins for Relays
## Currently, the only Relay is on Pin 24
GPIO.setup(24, GPIO.OUT)

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
			client.close()
			time.sleep(3.0)
		#Addition
		#keyCheckResult = checkKey(keys,barcode.data.decode("utf-8"))
		#print(keyCheckResult)
		#TODO: Set green LED on and trigger Relais to open box if True
		# Turn red LED on otherwise
		#Iterate over all known boxes
	
