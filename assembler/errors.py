# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		errors.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		17th December 2018
#		Purpose :	Error classes
#
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
#								Compiler Error
# ***************************************************************************************

class AssemblerException(Exception):
	def __init__(self,message):
		self.message = message
	def get(self):
		return "{0} ({1}:{2})".format(self.message,AssemblerException.FILENAME,AssemblerException.LINENUMBER)

AssemblerException.FILENAME = "test"
AssemblerException.LINENUMBER = 42

if __name__ == "__main__":
	ex = AssemblerException("Division by 42 error")
	print(ex.get())
	raise ex
	