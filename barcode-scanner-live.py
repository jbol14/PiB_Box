import cv2
from pyzbar import pyzbar
import imutils
from imutils.video import VideoStream
import time
from box import Box
import socket
import os
import json

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

SOCKETFILE = "/tmp/unix.sock"


	

boxes = [Box(1,"secretKey"),Box(2),Box(3,"anotherKey",["secret"]),Box(4,"AmericanDreamDenial",["key"])]

#TODO: Create proper Class for Boxes, that can compare Keys
# and knows which Pin to trigger
def checkKey(keys,key):
	for k in keys:
		if key == k:
			return True
	return False

keys = ["secret","key"]

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
	
			print("Connected to Socket")

			req = {
			"type" : "CHECK",
			"key" : key
			}
						
			client.send(json.dumps(req).encode("UTF-8"))
						

			data = client.recv(1024).decode("UTF-8")

			print(data)

			
			dataDict = json.loads(data)
			if dataDict != {}:
				GPIO.output(23, GPIO.HIGH)
				time.sleep(5)
				GPIO.output(23, GPIO.LOW)
				time.sleep(10)
			client.close()
		#Addition
		#keyCheckResult = checkKey(keys,barcode.data.decode("utf-8"))
		#print(keyCheckResult)
		#TODO: Set green LED on and trigger Relais to open box if True
		# Turn red LED on otherwise
		#Iterate over all known boxes
	
