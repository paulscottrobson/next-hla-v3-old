# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		term.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		16th December 2018
#		Purpose :	Extract a term from a stream
#
# ***************************************************************************************
# ***************************************************************************************

from errors import *
from streams import *
from elements import *
from dictionary import *
from democodegen import *
import os,re

# ***************************************************************************************
#						Extract a term. Returns [isAddress,address]
# ***************************************************************************************

class TermExtractor(object):
	def __init__(self,parser,codeGenerator,dictionary):
		self.parser = parser
		self.codeGenerator = codeGenerator
		self.dictionary = dictionary
	#
	#		Extract a tern
	#
	def extract(self):
		element = self.parser.get()
		#print("["+element+"]")
		#
		#		Nothing
		#
		if element == "":
			raise AssemblerException("Missing term")
		#
		#		- <Constant term>
		#
		if element == "-":
			term = self.extract()
			if term[0]:
				print("Can only apply unary minus to constants")
			term[1] = (-term[1]) & 0xFFFF
			return term
		#
		#		Constant integer. Also hex and 'character', the parser handles this.
		#
		if element[0] >= '0' and element[0] <= '9':
			return [False,int(element,10)]
		#
		#		Identifier.
		#
		if element[0] >= 'a' and element[0] <= 'z':
			dEntry = self.dictionary.find(element)
			if dEntry is None:
				raise AssemblerException("Unknown identifier "+element)
			if isinstance(dEntry,ConstantIdentifier):
				return [False,dEntry.getValue()]
			if isinstance(dEntry,VariableIdentifier):
				return [True,dEntry.getValue()]
			raise AssemblerException("Cannot use "+element+" in expression.")
		#
		#		Identifier address.
		#
		if element[0] == '@':
			element = self.parser.get()
			dEntry = self.dictionary.find(element)
			if dEntry is None:
				raise AssemblerException("Unknown identifier "+element)
			if isinstance(dEntry,VariableIdentifier):
				return [False, dEntry.getValue() & 0xFFFF]
			raise AssemblerException("Cannot use @ operator on "+element)
		#
		#		String
		#
		if element[0] == '"':
			strAddr = self.codeGenerator.stringConstant(element[1:-1])
			return [False,strAddr]
		#
		#		Give up !
		#
		raise AssemblerException("Bad term "+element)


if __name__ == "__main__":
	tas = TextArrayStream("""
		$7FFE 65321 'x' -4 38
		locvar glbvar const1 -const1
		"hello world"
		// String
		// @identifier (var only)

	""".split("\n"))

	tx = TermExtractor(ElementParser(tas),DemoCodeGenerator(),TestDictionary())
	while True:
		print(tx.extract())
