# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		expression.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		16th December 2018
#		Purpose :	Expression compiler
#
# ***************************************************************************************
# ***************************************************************************************

from errors import *
from streams import *
from elements import *
from dictionary import *
from democodegen import *
from term import *

# ***************************************************************************************
#								Expression Compiler
# ***************************************************************************************

class ExpressionCompiler(object):
	def __init__(self,parser,codeGenerator,dictionary):
		self.parser = parser
		self.codeGenerator = codeGenerator
		self.dictionary = dictionary
		self.termExtractor = TermExtractor(parser,codeGenerator,dictionary)

	def compile(self):
		firstTerm = self.termExtractor.extract()						# Get first term
		self.codeGenerator.loadARegister(firstTerm)						# Load in code
		operator = self.parser.get()									# See what's next
		while len(operator) == 1 and "+-*%!?&|^".find(operator) >= 0:	# Is it a known operator
			secondTerm = self.termExtractor.extract()					# Get the second term
			self.codeGenerator.binaryOperation(operator,secondTerm)		# Do the operation
			operator = self.parser.get() 								# See what follows
		self.parser.put(operator)										# Put unknown element back
		
if __name__ == "__main__":
	tas = TextArrayStream("""
		locvar + 4 < 7 
		glbvar!0?const1
		glbvar % locvar
	""".split("\n"))

	tx = ExpressionCompiler(ElementParser(tas),DemoCodeGenerator(),TestDictionary())
	tx.compile()
	print("===========================")
	tx.compile()
	print("===========================")
	tx.compile()
