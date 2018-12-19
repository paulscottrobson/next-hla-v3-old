# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		term.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		17th December 2018
#		Purpose :	Extract a term from a stream
#
# ***************************************************************************************
# ***************************************************************************************

from errors import *
from textparser import *
from streams import *
from dictionary import *
from democodegen import *

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
			return None
		#
		#		- [Constant term]
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
			return [False,int(element,10) & 0xFFFF]
		#
		#		Identifier.
		#
		if element[0] >= 'a' and element[0] <= 'z':
			dEntry = self.dictionary.find(element)
			if dEntry is None:
				raise AssemblerException("Unknown identifier "+element)
			if isinstance(dEntry,ConstantIdentifier):
				term = [False,dEntry.getValue()]
			elif isinstance(dEntry,VariableIdentifier):
				term = [True,dEntry.getValue()]
			else:
				raise AssemblerException("Cannot use "+element+" in expression.")
			return term
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
		self.parser.put(element)
		return None

if __name__ == "__main__":
	tas = TextArrayStream("""
		$7FFE 65321 'x' -4 38
		locvar glbvar const1 -const1
		"hello world" locvar!3 glbvar!locvar
		// String
		// @identifier (var only)

	""".split("\n"))

	p = TextParser(tas)
	tx = TermExtractor(p,DemoCodeGenerator(),TestDictionary())
	while True:
		print(tx.extract())
