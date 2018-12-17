# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		streams.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		16th December 2018
#		Purpose :	Stream input classes
#
# ***************************************************************************************
# ***************************************************************************************

from errors import *
import os

# ***************************************************************************************
#									Base stream class
# ***************************************************************************************

class Stream(object):
	def __init__(self):
		self.inQueue = None
	#
	#		Next character get
	#
	def get(self):
		if self.inQueue is not None:									# Single character put back
			ch = self.inQueue
			self.inQueue = None 
		else:															# if empty, use raw method
			ch = self.getRaw()
		return ch 
	#
	#		Put character back
	#
	def put(self,ch):
		assert self.inQueue is None,"put to stream twice"
		self.inQueue = ch
	#
	#		Set name, line number
	#
	def setFileName(self,fileName):
		AssemblerException.FILENAME = fileName
	def setLineNumber(self,lineNumber):
		AssemblerException.LINENUMBER = lineNumber

# ***************************************************************************************
#						Stream with information in text array
# ***************************************************************************************

class TextArrayStream(Stream):
	def __init__(self,textArray):
		Stream.__init__(self)
		self.setFileName("<textarray>")
		self.setLineNumber(1)
		self.currentLine = 0
		self.currentPos = 0
		textArray = [x if x.find("//") < 0 else x[:x.find("//")] for x in textArray]
		self.textArray = [x.strip()+" " for x in textArray]
		#print(self.textArray)

	def getRaw(self):
		if self.currentLine >= len(self.textArray):
			return ""
		if self.currentPos >= len(self.textArray[self.currentLine]):
			self.currentPos = 0
			self.currentLine += 1
			self.setLineNumber(self.currentLine+1)
		if self.currentLine >= len(self.textArray):
			return ""
		ch = self.textArray[self.currentLine][self.currentPos]
		self.currentPos += 1
		return ch

# ***************************************************************************************
#							Stream with information in file
# ***************************************************************************************

class FileStream(TextArrayStream):
		def __init__(self,fileName):
			if not os.path.isfile(fileName):
				self.setLineNumber(0)
				self.setFileName(fileName)
				raise AssemblerException("File not found")
			h = open(fileName,"r")
			TextArrayStream.__init__(self,h.readlines())
			h.close()

if __name__ == "__main__":
	tas = TextArrayStream("""
		$7FFE
		"hello" 123 // comment
		"world" 'x'
	
	""".split("\n"))

	#tas = FileStream("errors.py")

	c = tas.get()
	while c != "":
		print(c,ord(c))
		c = tas.get()

