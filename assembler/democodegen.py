# ***************************************************************************************
# ***************************************************************************************
#
#		Name : 		democodegenerator.py
#		Author :	Paul Robson (paul@robsons.org.uk)
#		Date : 		17th December 2018
#		Purpose :	Imaginary language code generator.
#
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
#
#					Code generator for an imaginary CPU, for testing
#
# ***************************************************************************************

class DemoCodeGenerator(object):
	def __init__(self,optimise = False):
		self.addr = 0x1000						# code space
		self.memoryAddr = 0x3000 				# uninitialised data
		self.opNames = {}
		for op in "+add;-sub;*mult;/div;%mod;&and;|or;^xor".split(";"):
			self.opNames[op[0]] = op[1:]
		self.jumpTypes = { "":"jmp","#":"jnz","=":"jz","+":"jpe","-":"jmi" }
	#
	#		Get current address in code space.
	#
	def getAddress(self):
		return self.addr
	#
	#		Allocate memory for a variable.
	#
	def allocate(self,count = 1):
		address = self.memoryAddr
		for i in range(0,count):
			print("${0:06x} : dw    0".format(self.memoryAddr))	
			self.memoryAddr += 2
		return address
	#
	#		Place an ASCIIZ string constant ... somewhere .... return its address
	#
	def stringConstant(self,str):
		print("${0:06x} : db    '{1}',0".format(self.addr,str))		# can be inline, or elsewhere
		addr = self.addr
		self.addr = self.addr + len(str) + 1
		return addr
	#
	#		Load Accumulator with constant or term.
	#
	def loadARegister(self,term):
		if term[0]:
			print("${0:06x} : ldr   a,(${1:04x})".format(self.addr,term[1]))
		else:
			print("${0:06x} : ldr   a,#${1:04x}".format(self.addr,term[1]))
		self.addr += 1
	#
	#		Perform a binary operation with a constant/term on the accumulator.
	#
	def binaryOperation(self,operator,term):
		if operator == "!" or operator == "?":							# indirect, we do add then read
			self.binaryOperation("+",term)								# add will optimise a bit
			print("${0:06x} : ldr.{1} a,[a]".format(self.addr,"w" if operator == "!" else "b"))
			self.addr += 1
			return
		operator = self.opNames[operator]								# convert op to opcode name
		if term[0]:
			print("${0:06x} : {1:4}  a,(${2:04x})".format(self.addr,operator,term[1]))
			self.addr += 1
		else:
			print("${0:06x} : {1:4}  a,#${2:04x}".format(self.addr,operator,term[1]))
			self.addr += 1
	#
	#		Save A at the address given
	#
	def saveDirect(self,address):
		print("${0:06x} : str   a,(${1:04x})".format(self.addr,address))
		self.addr += 1
	#
	#		Save temp register indirect through A, byte or word, and put temp back in A
	#
	def saveTempIndirect(self,isWord):
		print("${0:06x} : str.{1} b,[a]".format(self.addr," " if isWord else "b"))
		print("${0:06x} : tba".format(self.addr+1))	
		self.addr += 2
	#
	#		Copy A to the temp register, A value unknown after this.	
	#
	def copyToTemp(self):
		print("${0:06x} : tab".format(self.addr))
		self.addr += 1
	#
	#		Compile a call to a procedure (call should protect 'A')
	#
	def callProcedure(self,address):
		print("${0:06x} : call  ${1:06x}".format(self.addr,address))
		self.addr += 1
	#
	#		Compile a jump with the given condition ( "", "=", "#", "+" "-""). The
	#		target address is not known yet.
	#
	def compileJump(self,condition):
		assert condition in self.jumpTypes
		print("${0:06x} : {1:3}   ?????".format(self.addr,self.jumpTypes[condition]))
		jumpAddr = self.addr
		self.addr += 1
		return jumpAddr
	#
	#		Patch a jump given its base addres
	#
	def patchJump(self,jumpAddr,target):
		print("${0:06x} : (Set target to ${1:06x})".format(jumpAddr,target))
	#
	#		Compile the top of a for loop.
	#
	def forTopCode(self,indexVar):
		loop = self.getAddress()
		print("${0:06x} : dec   a".format(self.addr))					# decrement count
		print("${0:06x} : push  a".format(self.addr+1))					# push on stack
		self.addr += 2
		if indexVar is not None:										# if index exists put it there
			self.saveDirect(indexVar.getValue())
		return loop
	#
	#		Compile the bottom of a for loop
	#
	def forBottomCode(self,loopAddress):
		print("${0:06x} : pop   a".format(self.addr))					# pop off stack, jump if not done
		print("${0:06x} : jnz   ${1:06x}".format(self.addr+1,loopAddress))
		self.addr += 2
