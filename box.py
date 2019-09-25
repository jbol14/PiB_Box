class Box(object):
	def __init__(self,pinNumber, owner=None,guest=[]):
		self.ownerKey = owner
		self.guestKeys = guest
		self.pin = pinNumber
	def setOwnerKey(self,key):
		self.ownerKey = key

	def addHuestKey(self,key):
		self.guestKeys.append(key)

	def checkKey(self,key):
		if self.ownerKey == key:
			return True
		elif key in self.guestKeys:
			return True
		return False
