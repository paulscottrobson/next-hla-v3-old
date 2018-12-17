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
	def compile(self,parser):
		self.parser = parser
		self.termExtractor = TermExtractor(parser,self.codeGenerator,self.dictionary)
		self.compileSet("")
	#
	#		Compile a single item
	#
	def compileSet(self,exitOn):
		nextElement = self.parser.get()
		while nextElement != "" and nextElement != exitOn:
			#
			#		Normal binary operators + - * / % & | ^ ! ?
			#
			if len(nextElement) == 1 and "+-*/&|^%?!".find(nextElement) >= 0:		
				term = self.termExtractor.extract()									# get the term
				self.codeGenerator.binaryOperation(nextElement,term)				# and do the operation.
			#
			#		Assignment binary operation.
			#
			elif nextElement == ">":												
				self.assignment()
			# TODO Structures
			# TODO Variables
			# TODO Definitions
			# TODO Groups
			#
			#		Procedure
			#
			elif isinstance(self.dictionary.find(nextElement),ProcedureIdentifier):	
				self.procedureInvoke(self.dictionary.find(nextElement))
			else:																	# Not identified.
				self.parser.put(nextElement)										# put it back
				term = self.termExtractor.extract() 								# get a term
				self.codeGenerator.loadARegister(term) 								# and load it in.

			nextElement = self.parser.get()
	#
	#		Assignment.
	#
	def assignment(self):
		nextElement = self.parser.get()
		if nextElement == "(":														# indirect read/write ?
			termLeft = self.termExtractor.extract() 								# left side.
			operator = self.parser.get() 											# get operator, must be ! or ?
			if operator != "?" and operator != "!":
				raise AssemblerException("Bad operator for indirect assignment")
			termRight = self.termExtractor.extract() 								# right side.
			self.parser.expect(")")													# closing bracket
			self.codeGenerator.copyToTemp()	 										# copy the data to temp
			self.codeGenerator.loadARegister(termLeft)								# build up the indirect address
			self.codeGenerator.binaryOperation("+",termRight)
			self.codeGenerator.saveTempIndirect(operator == "!") 					# and save via it.
		else: 																		# direct read write
			self.parser.put(nextElement)
			term = self.termExtractor.extract()
			if not term[0]:															# must write to an address
				raise AssemblerException("Can only assign to an address")
			self.codeGenerator.saveDirect(term[1]) 									# write code to do so.
	#
	#		Call a procedure
	#
	def procedureInvoke(self,procIdentifier):
		self.parser.expect("(")
		currentParameterAddress = procIdentifier.getParameterBaseAddress() 			# get base address and count
		paramCount = procIdentifier.getParameterCount()
		while paramCount != 0:														# until all done.
			self.compileSet(")" if paramCount == 1 else ",") 						# compile until ) or , found
			self.codeGenerator.saveDirect(currentParameterAddress) 					# save that code
			currentParameterAddress += 2 											# next parameter
			paramCount -= 1
		self.codeGenerator.compileCall(procIdentifier.getValue())					# compile the actual call

if __name__ == "__main__":
	tas = TextArrayStream("""
		locvar+const1-glbvar*42&'a'>locvar
		const1>(locvar!4)
		const1>(locvar?glbvar)
		hello($101,$202,locvar+$303)
		42 >locvar
	""".split("\n"))

	p = TextParser(tas)
	cm = Compiler(TestDictionary(),DemoCodeGenerator())
	cm.compile(p)