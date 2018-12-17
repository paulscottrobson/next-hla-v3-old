# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		instruction.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		16th December 2018
#		Purpose :	Assemble a single instruction or instruction group.
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
import sys

# ***************************************************************************************
#
#						Compile one instruction or instruction group
#
# ***************************************************************************************

class InstructionCompiler(object):
	def __init__(self,parser,codeGenerator,dictionary):
		self.parser = parser
		self.codeGenerator = codeGenerator
		self.dictionary = dictionary
		self.termCompiler = TermExtractor(parser,codeGenerator,dictionary)
		self.expressionCompiler = ExpressionCompiler(parser,codeGenerator,dictionary)
	#
	#		Compile a single instruction or instruction group.
	#
	def compile(self):
		element = self.parser.get()
		#
		#		Variable
		#
		if element == "var":
			self.createVariable(True)
			return
		#
		#		If / While. While is an If with a jump up to the top.
		#
		if element == "while" or element == "if":						# Handle IF/WHILE
			self.ifWhile(element == "if")
			return
		#
		#		For loop
		#
		if element == "for":
			self.forLoop() 												# Handle FOR loop
			return
		#
		#		Empty instruction
		#
		if element == ";":												# Ignore ; on its own
			return
		#
		#		Instruction set grouped with {}
		#
		if element == "{":
			nextElement = self.parser.get() 							# Look at next instruction
			while nextElement != "}": 									# Keep going till }
				self.parser.put(nextElement) 							# Shove back
				self.compile() 											# Compile
				nextElement = self.parser.get()							# Examine next element.
			return
		#
		#		Check for assignment/procedure call.
		#
		if element[0] < 'a' or element[0] > 'z':
			raise AssemblerException("Syntax error "+element)
		#
		# 		Get the thing after the element and decide what to do based on it.
		#
		nextElement = self.parser.get()									# Get the element after the identifier
		self.parser.put(nextElement) 									# put them both back
		self.parser.put(element)
		if nextElement == "!" or nextElement == "?": 					# handle byte/word indirection
			self.indirectAssignment()
		elif nextElement == "=":										# handle direct assignment
			self.directAssignment()
		elif nextElement == "(":										# handle procedure call.
			self.procedureCall()
		else:
			raise AssemblerException("Syntax error "+element)		
	#
	#		Compile a direct assignment
	#
	def directAssignment(self):
		lExprName = self.parser.get()									# identifier to assign to
		lExpr = self.dictionary.find(lExprName)							# see if it exists
		if lExpr is None or not isinstance(lExpr,AddressIdentifier): 	# error if not, wrong type
			raise AssemblerException("Cannot assign to "+lExprName)
		self.parser.expect("=")											# =
		self.expressionCompiler.compile() 								# some expression
		self.parser.expect(";")
		self.codeGenerator.saveDirect(lExpr.getValue())					# save expression result
	#
	#		Compile an indirect assignment.
	#
	def indirectAssignment(self):
		lExprName = self.parser.get() 									# LHS of l-expr
		lExpr = self.dictionary.find(lExprName) 						# check it
		if lExpr is None or not isinstance(lExpr,AddressIdentifier):
			raise AssemblerException("Cannot assign to "+lExprName)
		operator = self.parser.get() 									# get the operator, already know ! or ?
		rTerm = self.termCompiler.extract()								# get the next term.
		self.codeGenerator.loadARegister([True,lExpr.getValue()]) 		# load the LHS in
		self.codeGenerator.binaryOperation("+",rTerm) 					# add the term to it.
		self.codeGenerator.copyToIndex() 								# put in index 
		self.parser.expect("=") 										# do the RHS
		self.expressionCompiler.compile()
		self.parser.expect(";")
		self.codeGenerator.saveIndirect(operator == "!")				# and save it as byte/word
	#
	#		Compile a procedure call
	#
	def procedureCall(self):
		procName = self.parser.get()									# get proc name, check it
		proc = self.dictionary.find(procName)
		if proc is  None or not isinstance(proc,AddressIdentifier):
			raise AssemblerException("Cannot call "+procName)
		self.parser.expect("(") 										# can't be missed out.
		for i in range(0,proc.getParameterCount()):						# for each parameter
			self.expressionCompiler.compile()							# compile and save
			self.codeGenerator.saveDirect(proc.getParameterBaseAddress()+i*2)
			if i < proc.getParameterCount()-1:							# check , if there is one
				self.parser.expect(",")
		self.parser.expect(")")											# end of proc call
		self.parser.expect(";")
		self.codeGenerator.compileCall(proc.getValue())					# compile the actual call.
	#
	#		Do If/While. While is just If with a loop back at the end :)
	#
	def ifWhile(self,isIf):
		condition = self.parser.get()									# condition, + (>= 0) - (<0) = (=0)
		if condition == "(":											# if none, default to # (<>0)
			self.parser.put(condition)
			condition = "#"
		if "#=+-".find(condition) < 0:									# validate it
			raise AssemblerException("Unknown condition on structure "+condition)
		condition = "=#-+"["#=+-".find(condition)]						# reverse it, skip if not true
		loopAddress = self.codeGenerator.getAddress()					# top loop for while
		self.parser.expect("(")											# do the condition
		self.expressionCompiler.compile()
		self.parser.expect(")")
		jumpAddress = self.codeGenerator.compileJump(condition)			# jump if failed.
		self.compile()													# compile the instruction
		if not isIf:													# for while
			loopJump = self.codeGenerator.compileJump("") 				# go back to the top.
			self.codeGenerator.patchJump(loopJump,loopAddress)
																		# patch the 'skip over'
		self.codeGenerator.patchJump(jumpAddress,self.codeGenerator.getAddress())
	#
	#		Compile FOR loop
	#
	def forLoop(self):
		self.parser.expect("(")											# do the count.
		self.expressionCompiler.compile()									
		self.parser.expect(")")
		index = self.dictionary.find("index")							# do we have an index
		if index is not None:
			if not isinstance(index,AddressIdentifier):
				raise AssemblerException("Cannot use index as defined")
																		# Top of loop
		forLoop = self.codeGenerator.forTopCode(index.getValue() if index is not None else None)
		self.compile()													# code that's repeated
		self.codeGenerator.forBottomCode(forLoop)						# bottom of loop.
	#
	#		Define a variable from the stream.
	#
	def createVariable(self,isLocal):
		identifier = self.parser.get() 									# get the identifier name.
		if identifier == "" or identifier[0] < 'a' or identifier[0] > 'z':
			raise AssemblerException("Bad identifier name "+identifier)
		if identifier.find(":") >= 0:									# <name>:<type>
			identifier = identifier.split(":")
			if len(identifier) != 2 or identifier[0] == "" or identifier[1] == "":
				raise AssemblerException("Bad type identifier")
			idtype = identifier[1]
			identifier = identifier[0]
		else: 															# just name
			idtype = None
		nextElement = self.parser.get()

		if nextElement == "[":											# memory allocated ?
			sizeTerm = self.termCompiler.extract()						# get how much
			if sizeTerm[0]:												# must be constant
				raise AssemblerException("Memory allocated must be a constant.")
			identValue = sizeTerm[1] 									# number of bytes
			if identValue == 0 or identValue > 8192:					# check validity of memory reqd.
				raise AssemblerException("Cannot allocate that amount of memory")
			identValue = self.codeGenerator.allocate(identValue)		# allocate memory for it.
			varAddr = self.codeGenerator.compileVariable(identValue)	# create a variable to refer to it.
			self.parser.expect("]")
		else:															# allocate word space
			self.parser.put(nextElement)								# (locals)
			varAddr = self.codeGenerator.allocate(2) 				
		self.parser.expect(";")
																		# add to dictionary.
		self.dictionary.add(VariableIdentifier(identifier,varAddr,idtype,not isLocal))

if __name__ == "__main__":
	tas = TextArrayStream("""
		var test:madeup[12];
		var fred;
		var sprites[1024];
		var return;

		proc myproc(a,b,c) {
			return = a+b+c;
		}
	""".split("\n"))

	tx = InstructionCompiler(ElementParser(tas),DemoCodeGenerator(),TestDictionary())
	tx.compile()
