from pin import Pin
from box import Box
import json
import os

CONFIG_PATH = "./Configuration/boxes.json"

## Frei verfügbare GPIO-Pins
pins = [4,14,15,17,18,27,22,23,24,10,9,25,11,8,7,1,0,5,6,12,13,19,16,26,21]

## Wie viele Boxen gibt es in diesem Cluster
#anzahlBoxen = input()
anzahlBoxen = 20
## Enthält am Ende alle verfügbaren Boxen
availableBoxes = []

## Hier merken wir uns welche Box-Nummern bereits vergeben wurden
usedBoxes = []

counter = 0

while counter < len(pins)-1:
    
    print("Pin {} was activated\nPlease enter the Number of the Box that was opened\nIf no Box opened up, please enter 0".format(pins[counter]))
    try:
        boxNumber = int(input())

        if boxNumber == 0:
            counter += 1

        elif boxNumber not in usedBoxes:
        
            usedBoxes.append(boxNumber)

            availableBoxes.append(Box(boxNumber,Pin(pins[counter])))

            counter += 1
    
        else:

            print("Another Pin was already assigned to Box {}".format(boxNumber))
    except ValueError:
        print("Please Enter a valid number between 1 and 20")
bx = {
    "available" : [],
    "used" :[]
}

for box in availableBoxes:
    bx["available"].append(box.toDict())

print(json.dumps(bx))

file = open(CONFIG_PATH,"w")

file.write(json.dumps(bx))

file.close()


    
