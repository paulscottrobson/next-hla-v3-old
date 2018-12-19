# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		parser.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		17th December 2018
#		Purpose :	Element parsing class
#
# ***************************************************************************************
# ***************************************************************************************

from errors import *
from streams import *

# ***************************************************************************************
#									Element parser
# ***************************************************************************************

class TextParser(object):
	def __init__(self,stream):
		self.stream = stream
		self.elementQueue = []
	#
	#		Get the next element
	#
	def get(self):
		if len(self.elementQueue) > 0:									# If something put back use that
			element = self.elementQueue[0]
			self.elementQueue = self.elementQueue[1:]
			return element
		ch = self.stream.get().lower()									# Get first character
		while ch == " ":												# Skip over spaces.
			ch = self.get()
		#
		#		Quoted string
		#
		if ch == '"':													# "<string>"
			string = ""
			ch = self.stream.get()										# rip the string out.
			while ch != '"':
				if ch == "":
					raise AssemblerException("Missing closing quote for string")
				string = string + ch
				ch = self.stream.get()
			return '"'+string+'"'
		#
		#		Integer
		#
		if ch >= '0' and ch <= '9':										# decimal integer
			number = ch													# rip and convert
			ch = self.stream.get()
			while ch >= "0" and ch <= "9":
				number = number + ch
				ch = self.stream.get()
			self.stream.put(ch)
			return number
		#
		#		Hex Integer
		#
		if ch == '$':													# hexadecimal integer (converted to decimal)
			word = ""
			ch = self.stream.get().lower()
			while (ch >= '0' and ch <= '9') or (ch >= 'a') and (ch <= 'f'):
				word = word + ch
				ch = self.stream.get().lower()
			self.stream.put(ch)
			return str(int(word,16) & 0xFFFF)
		#
		#		Identifier
		#
		if (ch >= 'a' and ch <= 'z') or ch == '_':						# identifier
			ident = ch
			ch = self.stream.get().lower()								# get the full identifier
			while (ch >= 'a' and ch <= 'z') or (ch >= '0' and ch <= '9') or ch == '.' or ch == '_' or ch == ':':
				ident = ident + ch
				ch = self.stream.get().lower()
			self.stream.put(ch)											# put back the unknown
			return ident
		#
		#		Quoted single character
		#
		if ch == "'":													# single character (converted to decimal)
			char = self.stream.get()
			ch = self.stream.get()
			if ch != "'":
				raise AssemblerException("")
			return str(ord(char))										# we convert it to an integer
		#
		#		Special case of '->' mapped onto >
		#
		if ch == "-":
			ch = self.stream.get()
			if ch != ">":
				self.stream.put(ch)
				ch = "-"
		return ch	
		
	#
	#		Put the next element back
	#
	def put(self,element):
		self.elementQueue.insert(0,element)
	#
	#		Test the next element to see if it's what we want.
	#
	def expect(self,element):
		if self.get() != element.lower():
			raise AssemblerException("Missing "+element+" in source code.")

if __name__ == "__main__":
	tas = TextArrayStream("""
		$7FFE
		locvar:test + 4 ;
		"hello" 123 var.ident_1 >+< 'x' // comment
		"world" $2A [42]
	
	""".split("\n"))

	#tas = FileStream("errors.py")

	pars = TextParser(tas)
	c = pars.get()
	while c != "":
		print(c)
		c = pars.get()
