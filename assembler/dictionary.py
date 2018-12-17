# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		dictionary.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		17th December 2018
#		Purpose :	Dictionary Class
#
# ***************************************************************************************
# ***************************************************************************************

from identifiers import *
from errors import *

# ***************************************************************************************
#									Dictionary class
# ***************************************************************************************

class Dictionary(object):
	def __init__(self):
		self.globals = {}
		self.locals = {}
	#
	#	Add an identifier to the dictionary.
	#
	def add(self,identifier):
		target = self.globals if identifier.isGlobal() else self.locals # decide where its going
		if identifier.getName() in target: 								# check for duplication
			raise AssemblerException("Duplicate idenifier "+identifier.getName())
		target[identifier.getName()] = identifier 						# store
	#
	#	Get an identifier from the dictionary.
	#
	def find(self,identifier):
		identifier = identifier.strip().lower()							# get ID
		if identifier in self.locals: 									# locals have priority
			return self.locals[identifier]
		if identifier in self.globals:									# over globals
			return self.globals[identifier]
		return None
	#
	#	Purge all locals
	#
	def purgeLocals(self):
		self.locals = {}
	#
	#	Purge at end of module ; all locals and any identifier beginning with an underscore
	#
	def purgeEndModule(self):
		self.purgeLocals()
		globals = self.globals
		self.globals = {}
		for key in [x for x in globals.keys() if x[0] != '_']:
			self.globals[key] = globals[key]
	#
	#	Convert dictionary to text to print
	#
	def toString(self):
		return "Globals:\n"+self.toStringSub(self.globals)+"Locals:\n"+self.toStringSub(self.locals)
	#
	def toStringSub(self,dict):
		keys = [x for x in dict.keys()]
		keys.sort()
		return "\n".join(["\t{0}".format(dict[x].toString()) for x in keys])+"\n"

# ***************************************************************************************
#						This class has made up test data for testing
# ***************************************************************************************

class TestDictionary(Dictionary):
	def __init__(self):
		Dictionary.__init__(self)
		w = ProcedureIdentifier("hello",0x123456,0xFF02,3)
		self.add(w)
		self.add(VariableIdentifier("locvar",0x1234,False))
		self.add(VariableIdentifier("glbvar",0x5678,True))
		self.add(ConstantIdentifier("const1",0xABCD))


if __name__ == "__main__":
	td = TestDictionary()
	print("0-----------------------------------------")
	print(td.toString())
	print("1-----------------------------------------")
	td.purgeLocals()
	print(td.toString())
	print("2-----------------------------------------")
	td.purgeEndModule()
	print(td.toString())
