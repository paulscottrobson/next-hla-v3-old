# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		assembler.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		19th December 2018
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
#									Main assembler
# ***************************************************************************************

class Assembler(object):
	def __init__(self,dictionary,codeGenerator):
		self.dictionary = dictionary
		self.codeGenerator = codeGenerator
	#
	#		New compilation
	#
	def assembleSource(self,parser):
		self.parser = parser
		self.termExtractor = TermExtractor(parser,self.codeGenerator,self.dictionary)
		if self.assemble() != "":
			raise AssemblerException("Syntax Error")
	#
	#		assemble a full parser source.
	#
	def assemble(self):
		while True:
			print("==============================")
			error = self.assembleInstruction()
			if error is not None:
				return error
	#
	#		assemble a single item.
	#
	def assembleInstruction(self):
		nextItem = self.parser.get()									# get next item
		ident = self.dictionary.find(nextItem) 							# look up in dictionary.
		#
		#		Code Group.
		#
		if nextItem == "{":												# found a {
			endGroup = self.assemble()									# assemble, should match a }
			if endGroup != "}":
				raise AssemblerException("Missing }")
			return None
		#
		# 		Structures
		#
		if nextItem == "for":
			self.forLoop()
			return None
		#
		# 		Global/Local variable definitions
		#
		if nextItem == "global" or nextItem == "local":
			varName = self.parser.get()
			if varName == "" or ((varName[0] < 'a' or varName[0] > 'z') and varName[0] != '_'):
				raise AssemblerException("Bad variable name")
			address = self.codeGenerator.allocate()
			self.dictionary.add(VariableIdentifier(varName,address,nextItem == "global"))
			return None
		#
		#		Procedure definition
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
			endChar = self.assemble() 	
			if endChar != (")" if paramCount == 1 else ","):			# should finish with , or )
				raise AssemblerException("Badly formed parameters")
			self.codeGenerator.saveDirect(paramAddress) 				# save whatever it was.
			paramCount -= 1 											# one fewer parameter.
			paramAddress += 2 
		self.codeGenerator.callProcedure(procIdent.getValue())			# compile procedure call.
	#
	#		Handle a for loop
	#
	def forLoop(self):
		self.parser.expect("(")											# ( opening the loop count
		endChar = self.assemble()										# expression to ) closing it
		if endChar != ")":
			raise AssemblerException("Missing ) in for")
		ixVar = self.dictionary.find("index")							# Look for a variable called index
		loop = self.codeGenerator.forTopCode(ixVar) 					# top of loop
		self.assembleInstruction() 										# body of loop
		self.codeGenerator.forBottomCode(loop) 							# bottom of loop

if __name__ == "__main__":
	tas = TextArrayStream("""
		locvar+5->locvar
		42+locvar>glbvar?2
		locvar!6+4
		locvar!glbvar+locvar?2 
		hello(locvar,glbvar?13,42)>locvar
		const1
		local n1 global n2
		n1+n2>n2>n1
		local index
		for (42) { n1+1>n1 }
	""".split("\n"))

	p = TextParser(tas)
	cm = Assembler(TestDictionary(),DemoCodeGenerator())
	cm.assembleSource(p)
	print(cm.dictionary.toString())