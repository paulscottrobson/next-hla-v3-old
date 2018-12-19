# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		compiler.py
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
from term import *

# ***************************************************************************************
#									Main Compiler
# ***************************************************************************************

class Compiler(object):
	def __init__(self,dictionary,codeGenerator):
		self.dictionary = dictionary
		self.codeGenerator = codeGenerator
	#
	#		New compilation
	#
	def compileSource(self,parser):
		self.parser = parser
		self.termExtractor = TermExtractor(parser,self.codeGenerator,self.dictionary)
		if self.compile() != "":
			raise AssemblerException("Syntax Error")
	#
	#		Compile a full parser source.
	#
	def compile(self):
		while True:
			print("==============================")
			error = self.compileInstruction()
			if error is not None:
				return error
	#
	#		Compile a single item.
	#
	def compileInstruction(self):
		nextItem = self.parser.get()									# get next item
		ident = self.dictionary.find(nextItem) 							# look up in dictionary.
		#
		# 		Structures
		#

		#
		# 		Global/Local variable definitions
		#

		#
		# 		Procedure call
		#
		if isinstance(ident,ProcedureIdentifier):
			self.callProcedure(ident)
			return None
		#
		# 		Binary operations
		#
		if len(nextItem) == 1 and "+-*/%&|^!?".find(nextItem) >= 0:
			term = self.termExtractor.extract() 						# get the operand.
			if term is None:
				raise AssemblerException("Missing term")
			self.codeGenerator.binaryOperation(nextItem,term)			# generate the code for it
			return None
		#
		# 		Assignment
		#
		if nextItem == ">":
			self.binaryAssignment()
			return
		#
		# 		Is it a "Starter" Term - one that loads in a value.
		#
		self.parser.put(nextItem) 										# put it back
		term = self.termExtractor.extract() 							# try and grab a term.
		if term is not None:											# found one ?
			self.codeGenerator.loadARegister(term) 						# generate code to load a term in.
			return None 												# okay.
		
		return self.parser.get()
	#
	#		Do a binary assignment (>)
	#
	def binaryAssignment(self):
		term = self.termExtractor.extract() 							# where to save.
		if not term[0]:
			raise AssemblerException("Must assign to an address")
		nextItem = self.parser.get() 									# see if followed by ! or ?
		if nextItem == "?" or nextItem == "!":							# if so, it's an indirect save.
			rTerm = self.termExtractor.extract()						# get following term
			if rTerm is None:
				raise AssemblerException("Bad assignment")
			self.codeGenerator.copyToTemp() 							# save result
			self.codeGenerator.loadARegister(term) 						# calculate the address
			self.codeGenerator.binaryOperation("+",rTerm)
			self.codeGenerator.saveTempIndirect(nextItem == "!") 		# and write there.
		else:
			self.codeGenerator.saveDirect(term[1]) 						# store to memory
			self.parser.put(nextItem) 									# put last element back
	#
	#		Call a procedure.
	#
	def callProcedure(self,procIdent):
		self.parser.expect("(")											# check open bracket.
		paramCount = procIdent.getParameterCount()						# how many parameters ?
		paramAddress = procIdent.getParameterBaseAddress()				# where do they go ?
		while paramCount > 0:
			endChar = self.compile() 	
			if endChar != (")" if paramCount == 1 else ","):			# should finish with , or )
				raise AssemblerException("Badly formed parameters")
			self.codeGenerator.saveDirect(paramAddress) 				# save whatever it was.
			paramCount -= 1 											# one fewer parameter.
			paramAddress += 2 
		self.codeGenerator.compileCall(procIdent.getValue())

if __name__ == "__main__":
	tas = TextArrayStream("""
		locvar+5>locvar
		42+locvar>glbvar?2
		locvar!6+4
		locvar!glbvar+locvar?2 
		hello(locvar,glbvar?13,42)
		const1
	""".split("\n"))

	p = TextParser(tas)
	cm = Compiler(TestDictionary(),DemoCodeGenerator())
	cm.compileSource(p)