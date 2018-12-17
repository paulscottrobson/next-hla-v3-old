# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		modules.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		16th December 2018
#		Purpose :	Assemble a module.
#
# ***************************************************************************************
# ***************************************************************************************

from errors import *
from streams import *
from elements import *
from dictionary import *
from democodegen import *
from expression import *
from term import *
from instruction import *
import sys

# ***************************************************************************************
#
#						Compile one instruction or instruction group
#
# ***************************************************************************************

class ModuleCompiler(object):
	def __init__(self,parser,codeGenerator,dictionary):
		self.parser = parser
		self.codeGenerator = codeGenerator
		self.dictionary = dictionary
		self.instructionCompiler = InstructionCompiler(parser,codeGenerator,dictionary)
	#
	#		Compile a single instruction or instruction group.
	#
	def compile(self):
		nextElement = self.parser.get()
		while nextElement != "":
			if nextElement == "var":
				self.instructionCompiler.createVariable(False)
			elif nextElement == "proc":
				self.procedureDefinition()
			else:
				raise AssemblerException("Syntax error")
			nextElement = self.parser.get()
	#
	#		Define a procedure.
	#
	
if __name__ == "__main__":
	tas = TextArrayStream("""
		var test:madeup[12];
		var fred;
		var sprites[1024];

	""".split("\n"))

	tx = ModuleCompiler(ElementParser(tas),DemoCodeGenerator(),TestDictionary())
	tx.compile()

