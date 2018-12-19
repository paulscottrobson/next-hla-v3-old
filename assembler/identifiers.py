# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		identifiers.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		17th December 2018
#		Purpose :	Identifier classes
#
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
#								Root identifier class
# ***************************************************************************************

class Identifier(object):
	def __init__(self,name,value,isGlobal = True):
		self.name = name.strip().lower()
		self.value = value
		self.isGlobalIdentifier = isGlobal
	#
	def getName(self):
		return self.name
	def getValue(self):
		return self.value
	def isGlobal(self):
		return self.isGlobalIdentifier
	#
	def toString(self):
		return "{0} @ ${1:06x} '{3}' {2}".format(self.getName(),self.getValue(),	\
							"global" if self.isGlobalIdentifier else "local",self.getTypeName())

# ***************************************************************************************
#					Identifier representing a constant value
# ***************************************************************************************

class ConstantIdentifier(Identifier):
	def __init__(self,name,value):
		Identifier.__init__(self,name,value,True)						# Constants global
	def getTypeName(self):	
		return "ConstantIdentifier"

# ***************************************************************************************
#					Identifier representing an address
# ***************************************************************************************

class AddressIdentifier(Identifier):
	def getTypeName(self):
		return "AddressIdentifier"

# ***************************************************************************************
#						Identifier representing a variable
# ***************************************************************************************

class VariableIdentifier(AddressIdentifier):
	def getTypeName(self):
		return "VariableIdentifier"

# ***************************************************************************************
#					  Identifier representing a procedure
# ***************************************************************************************

class ProcedureIdentifier(AddressIdentifier):
	def __init__(self,name,address,paramAddress,paramCount):
		AddressIdentifier.__init__(self,name,address,True)
		self.paramAddress = paramAddress
		self.paramCount = paramCount
	def getTypeName(self):
		return "ProcedureIdentifier"
	def getParameterCount(self):
		return self.paramCount
	def getParameterBaseAddress(self):
		return self.paramAddress
	def toString(self):
		s = AddressIdentifier.toString(self)
		if self.getParameterCount() > 0:
			s = s + " ({0} params @ ${1:04x})".format(self.getParameterCount(),self.getParameterBaseAddress())
		return s

if __name__ == "__main__":
	w = ProcedureIdentifier("hello",0x123456,0x8011,2)
	print(w.toString())

