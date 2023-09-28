"""
#  b43 debugging library
#
#  Copyright (C) 2008-2010 Michael Buesch <mb@bu3sch.de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License version 3
#  as published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import re
import hashlib
from tempfile import *
import ctypes

CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h>

class timespec(ctypes.Structure):
	_fields_ = [
	('tv_sec', ctypes.c_long),
	('tv_nsec', ctypes.c_long)
	]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def monotonic_time():
	t = timespec()
	if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
		errno_ = ctypes.get_errno()
		raise OSError(errno_, os.strerror(errno_))
	#return t.tv_sec + t.tv_nsec * 1e-9\
	return t


class B43Exception(Exception):
	pass


B43_MMIO_MACCTL		= 0x120
B43_MMIO_PSMDEBUG	= 0x154

B43_MACCTL_PSM_MACEN	= 0x00000001
B43_MACCTL_PSM_RUN	= 0x00000002
B43_MACCTL_PSM_JMP0	= 0x00000004
B43_MACCTL_PSM_DEBUG	= 0x00002000

class B43PsmDebug:
	"""Parse the contents of the PSM-debug register"""
	def __init__(self, reg_content):
		self.raw = reg_content
		return

	def getRaw(self):
		"""Get the raw PSM-debug register value"""
		return self.raw

	def getPc(self):
		"""Get the microcode program counter"""
		return self.raw & 0xFFF


class B43:
	"""Hardware access layer. This accesses the hardware through the debugfs interface."""

	# SHM routing values
	B43_SHM_UCODE		= 0
	B43_SHM_SHARED		= 1
	B43_SHM_REGS		= 2
	B43_SHM_IHR		= 3
	B43_SHM_RCMTA		= 4

	#GPR definition
	GPR_MIN_CONTENTION_WIN	= 6
	GPR_MAX_CONTENTION_WIN	= 7
	GPR_CUR_CONTENTION_WIN  = 8
	#IPT=44

	#COUNT_FREEZING=26 #for openfwwf
	#COUNT_FREEZING=46 #for WMP

	#STATE_DEBUG_02	= 56
	#STATE_DEBUG_03	= 58

	PROCEDURE_REGISTER_1	= 44	#IPT
	PROCEDURE_REGISTER_2	= 46	#COUNT_FREEZING

	STATE_DEBUG_04	= 59

	GPR_CONTROL = 55

	BYTECODE_ADDR_OFFSET = 57

	#SHM offset position
	SHM_EDCFQ		= 0x240 # EDCF Q info
	SHM_EDCFQCUR	= 0x260 # EDCF info for the current (the only one!) queue
	SHM_EDCFQ_TXOP	= 0x00
	SHM_EDCFQ_CWMIN	= 0x02
	SHM_EDCFQ_CWMAX	= 0x04
	SHM_EDCFQ_CWCUR	= 0x06
	SHM_EDCFQ_AIFS	= 0x08
	SHM_EDCFQ_BSLOTS = 0x0A
	SHM_EDCFQ_REGGAP = 0x0C
	SHM_EDCFQ_STATUS = 0x0E # Informations about retries

	SHM_SLOT_1_TDMA_SUPER_FRAME_SIZE = 0x085C
	SHM_SLOT_1_TDMA_ALLOCATED_SLOT = 0x0872
	SHM_SLOT_1_TDMA_NUMBER_OF_SYNC_SLOT= 0x086E
	SHM_SLOT_1_TDMA_ALLOCATED_MASK_SLOT = 0x084E

	SHM_SLOT_2_TDMA_SUPER_FRAME_SIZE = 0x0C4C
	SHM_SLOT_2_TDMA_ALLOCATED_SLOT = 0x0C62
	SHM_SLOT_2_TDMA_NUMBER_OF_SYNC_SLOT = 0x0C5E
	SHM_SLOT_2_TDMA_ALLOCATED_MASK_SLOT = 0x0C3E


	#SYNC_AP_ADDRESS
	MAC_ADDR_SYNCHRONIZATION_AP_GPR = 40
	MAC_ADDR_SYNCHRONIZATION_AP = "MAC_ADDR_SYNCHRONIZATION_AP"



	#SHARE measurement
	#BUSY_TIME	= 0x0100
	BUSY_TIME_CHANNEL = 0x00DE
	BUSY_TIME_CHANNEL_HI = 0x00DE
	BUSY_TIME_CHANNEL_LO = 0x00E0

	#num freezing
	NUM_FREEZING_COUNT	=	0x0158

	TX_ACTIVITY_CHANNEL = 0x015A
	TX_ACTIVITY_HI = 0x015A
	TX_ACTIVITY_LO = 0x015C


	#TSF
	B43_MMIO_TSF_0			= 0x632
	B43_MMIO_TSF_1			= 0x634
	B43_MMIO_TSF_2			= 0x636
	B43_MMIO_TSF_3			= 0x638

	#TX frames tracing
	#define TX_COUNTER				SHM(0x0114)		in this moment, I use register for this variable
	#define TX_DATA_FRAME_COUNTER	SHM(0x0116)		in this moment, I use register for this variable
	#define RX_ACK_COUNTER			SHM(0x0118)		in this moment, I use register for this variable
	TX_COUNTER				= 0x0114
	RX_ACK_COUNTER			= 61
	TX_DATA_FRAME_COUNTER	= 62 #0x0116 register in this moment
	RX_ACK_COUNTER_RAMATCH	= 63 #0x0118 register in this moment

	#RX frames tracing
	RX_TOO_LONG_COUNTER 		= 0x0104		# RX Too Long (Limit is 2346 bytes)
	RX_TOO_SHORT_COUNTER 		= 0x0106		# RX Too Short (Not enough bytes for frame type)
	INVALID_MACHEADER_COUNTER 	= 0x0108   		# RX Invalid MAC Header (Either Protocol Version is not 0, or the frame type isn't Data, Control or Management)
	BAD_FCS_COUNTER 			= 0x010A		# RX Bad FCS (Frames where CRC Failed)
	BAD_PLCP_COUNTER			= 0x010C		# RX Bad PLCP (Parity Check of PLCP Header Failed)
	RX_CRS_GLITCH_COUNTER		= 0x010E		# RX CRS Glitch (Preamble is okay, but not the Header)

	GOOD_PLCP_COUNTER			= 0x0110		# RX Frames with good PLCP
	GOOD_FCS_MATCH_RA_COUNTER	= 60 #= 0x0112		# RX Data "Frames" with Good FCS and Matching RA //non sono solo data frame ma tutti i frame
	GOOD_FCS_NO_MATCH_RA_COUNTER= 0x011E		# RX Data "Frames" with Good FCS and not matching RA //non sono solo data frame ma tutti i frame
	GOOD_FCS_COUNTER			= 0x0150

	#Reference value offset
	PARAMETER_ADDR_OFFSET_BYTECODE_1	=	0x0418
	PARAMETER_ADDR_BYTECODE_1			=	0x0830
	PARAMETER_ADDR_OFFSET_BYTECODE_2	=	0x0610
	PARAMETER_ADDR_BYTECODE_2			=	0x0C20

	#*****************************
    #TDMA RADIO PROGRAM PARAMETERS
    #use setParameterLowerLayer to set value
    #use getParameterLowerLayer to get value
    #*****************************
	#implemented
	TDMA_SUPER_FRAME_SIZE 		= "TDMA_SUPER_FRAME_SIZE"
	TDMA_NUMBER_OF_SYNC_SLOT 	= "TDMA_NUMBER_OF_SYNC_SLOT"
	TDMA_ALLOCATED_SLOT 		= "TDMA_ALLOCATED_SLOT"
	#*****************************
    #CSMA RADIO PROGRAM PARAMETERS
    #use setParameterLowerLayer to set value
    #use getParameterLowerLayer to get value
    #*****************************
    #implemented
	CSMA_CW		= "CSMA_CW"
	CSMA_CW_MIN	= "CSMA_CW_MIN"
	CSMA_CW_MAX	= "CSMA_CW_MAX"
	#*****************************
    #RADIO MEASURAMENT
    #use getMonitor to get measurament value
    #*****************************
    #implemented
	NUM_TX			= "NUM_TX"
	NUM_TX_SUCCESS	= "NUM_TX_SUCCESS"

	NUM_RX			= "NUM_RX"
	NUM_RX_SUCCESS	= "NUM_RX_SUCCESS"
	NUM_RX_MATCH	= "NUM_RX_MATCH"

	BUSY_TYME		= "BUSY_TIME"
	TX_ACTIVITY		= "TX_ACTIVITY"

	"""
	COUNT_SLOT = "COUNT_SLOT"
	PACKET_TO_TRANSMIT = "PACKET_TO_TRANSMIT"
	MY_TRANSMISSION = "MY_TRANSMISSION"
	SUCCES_TRANSMISSION = "SUCCES_TRANSMISSION"
	OTHER_TRANSMISSION = "OTHER_TRANSMISSION"
	BAD_RECEPTION = "BAD_RECEPTION"
	BUSY_SLOT = "BUSY_SLOT"
    """
	COUNT_SLOT	=	43
	PACKET_TO_TRANSMIT	= 0x00F0
	MY_TRANSMISSION		= 0x00F2
	SUCCES_TRANSMISSION	= 0x00F4
	OTHER_TRANSMISSION	= 0x00F6
	BAD_RECEPTION		= 0x00FA
	BUSY_SLOT           = 0x00FC



	def __init__(self, phy=None):

		debugfs_path = self.__debugfs_find()

		# Construct the debugfs b43 path to the device
		b43_path = debugfs_path + "/b43/"
		if phy:
			b43_path += phy
		else:
			# Get the PHY.
			try:
				phys = os.listdir(b43_path)
			except OSError:
				print("Could not find B43's debugfs directory: %s" % b43_path)
				raise B43Exception
			if not phys:
				print("Could not find any b43 device")
				raise B43Exception
			if len(phys) != 1:
				print("Found multiple b43 devices.")
				print("You must call this tool with a phyX parameter to specify a device")
				raise B43Exception
			phy = phys[0]
			b43_path += phy;

		# Open the debugfs files
		try:
			self.f_mmio16read = open(b43_path + "/mmio16read", "r+")
			self.f_mmio16write = open(b43_path + "/mmio16write", "w")
			self.f_mmio32read = open(b43_path + "/mmio32read", "r+")
			self.f_mmio32write = open(b43_path + "/mmio32write", "w")
			self.f_shm16read = open(b43_path + "/shm16read", "r+")
			self.f_shm16write = open(b43_path + "/shm16write", "w")
			self.f_shm32read = open(b43_path + "/shm32read", "r+")
			self.f_shm32write = open(b43_path + "/shm32write", "w")
		except IOError as e:
			print("Could not open debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception

		self.b43_path = b43_path
		self.radio_platform_t = None
		self.event_list = []
		self.monitor_list = [self.NUM_TX, self.NUM_TX_SUCCESS, self.NUM_RX, self.NUM_RX_SUCCESS, self.NUM_RX_MATCH, self.BUSY_TYME, self.TX_ACTIVITY]
		self.param_list = [self.TDMA_SUPER_FRAME_SIZE, self.TDMA_NUMBER_OF_SYNC_SLOT, self.TDMA_ALLOCATED_SLOT, self.CSMA_CW, self.CSMA_CW_MIN, self.CSMA_CW_MAX]
		return

	# Get the debugfs mountpoint.
	def __debugfs_find(self):
		mtab = open("/etc/mtab").read().splitlines()
		regexp = re.compile(r"^[\w\-_]+\s+([\w/\-_]+)\s+debugfs")
		path = None
		for line in mtab:
			m = regexp.match(line)
			if m:
				path = m.group(1)
				break
		if not path:
			print("Could not find debugfs in /etc/mtab")
			raise B43Exception
		return path

	def read16(self, reg):
		"""Do a 16bit MMIO read"""
		try:
			self.f_mmio16read.seek(0)
			self.f_mmio16read.write("0x%X" % reg)
			self.f_mmio16read.flush()
			self.f_mmio16read.seek(0)
			val = self.f_mmio16read.read()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return int(val, 16)

	def read32(self, reg):
		"""Do a 32bit MMIO read"""
		try:
			self.f_mmio32read.seek(0)
			self.f_mmio32read.write("0x%X" % reg)
			self.f_mmio32read.flush()
			self.f_mmio32read.seek(0)
			val = self.f_mmio32read.read()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return int(val, 16)

	def maskSet16(self, reg, mask, set):
		"""Do a 16bit MMIO mask-and-set operation"""
		try:
			mask &= 0xFFFF
			set &= 0xFFFF
			self.f_mmio16write.seek(0)
			self.f_mmio16write.write("0x%X 0x%X 0x%X" % (reg, mask, set))
			self.f_mmio16write.flush()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return
	
	def write16(self, reg, value):
		"""Do a 16bit MMIO write"""
		self.maskSet16(reg, 0, value)
		return

	def maskSet32(self, reg, mask, set):
		"""Do a 32bit MMIO mask-and-set operation"""
		try:
			mask &= 0xFFFFFFFF
			set &= 0xFFFFFFFF
			self.f_mmio32write.seek(0)
			self.f_mmio32write.write("0x%X 0x%X 0x%X" % (reg, mask, set))
			self.f_mmio32write.flush()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return

	def write32(self, reg, value):
		"""Do a 32bit MMIO write"""
		self.maskSet32(reg, 0, value)
		return

	def shmRead16(self, routing, offset):
		"""Do a 16bit SHM read"""
		try:
			self.f_shm16read.seek(0)
			self.f_shm16read.write("0x%X 0x%X" % (routing, offset))
			self.f_shm16read.flush()
			self.f_shm16read.seek(0)
			val = self.f_shm16read.read()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return int(val, 16)

	def shmMaskSet16(self, routing, offset, mask, set):
		"""Do a 16bit SHM mask-and-set operation"""
		try:
			mask &= 0xFFFF
			set &= 0xFFFF
			self.f_shm16write.seek(0)
			self.f_shm16write.write("0x%X 0x%X 0x%X 0x%X" % (routing, offset, mask, set))
			self.f_shm16write.flush()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return

	def shmWrite16(self, routing, offset, value):
		"""Do a 16bit SHM write"""
		self.shmMaskSet16(routing, offset, 0, value)
		return

	def shmRead32(self, routing, offset):
		"""Do a 32bit SHM read"""
		try:
			self.f_shm32read.seek(0)
			self.f_shm32read.write("0x%X 0x%X" % (routing, offset))
			self.f_shm32read.flush()
			self.f_shm32read.seek(0)
			val = self.f_shm32read.read()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return int(val, 16)

	def shmMaskSet32(self, routing, offset, mask, set):
		"""Do a 32bit SHM mask-and-set operation"""
		try:
			mask &= 0xFFFFFFFF
			set &= 0xFFFFFFFF
			self.f_shm32write.seek(0)
			self.f_shm32write.write("0x%X 0x%X 0x%X 0x%X" % (routing, offset, mask, set))
			self.f_shm32write.flush()
		except IOError as e:
			print("Could not access debugfs file %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		return

	def shmWrite32(self, routing, offset, value):
		"""Do a 32bit SHM write"""
		self.shmMaskSet32(routing, offset, 0, value)
		return

	def getGprs(self):
		"""Returns an array of 64 ints. One for each General Purpose register."""
		ret = []
		for i in range(0, 64):
			val = self.shmRead16(B43_SHM_REGS, i)
			ret.append(val)
		return ret

	def getLinkRegs(self):
		"""Returns an array of 4 ints. One for each Link Register."""
		ret = []
		for i in range(0, 4):
			val = self.read16(0x4D0 + (i * 2))
			ret.append(val)
		return ret

	def getOffsetRegs(self):
		"""Returns an array of 7 ints. One for each Offset Register."""
		ret = []
		for i in range(0, 7):
			val = self.read16(0x4C0 + (i * 2))
			ret.append(val)
		return ret

	def shmSharedRead(self):
		"""Returns a string containing the SHM contents."""
		ret = ""
		for i in range(0, 4096, 4):
			val = self.shmRead32(B43_SHM_SHARED, i)
			ret += "%c%c%c%c" %	(val & 0xFF,
						 (val >> 8) & 0xFF,
						 (val >> 16) & 0xFF,
						 (val >> 24) & 0xFF)
		return ret

	def getPsmDebug(self):
		"""Read the PSM-debug register and return an instance of B43PsmDebug."""
		val = self.read32(B43_MMIO_PSMDEBUG)
		return B43PsmDebug(val)

	def getPsmConditions(self):
		"""This returns the contents of the programmable-PSM-conditions register."""
		return self.read16(0x4D8)

	def ucodeStop(self):
		"""Unconditionally stop the microcode PSM. """
		self.maskSet32(B43_MMIO_MACCTL, ~B43_MACCTL_PSM_RUN, 0)
		return

	def ucodeStart(self):
		"""Unconditionally start the microcode PSM. This will restart the
		microcode on the current PC. It will not jump to 0. Warning: This will
		unconditionally restart the PSM and ignore any driver-state!"""
		self.maskSet32(B43_MMIO_MACCTL, ~0, B43_MACCTL_PSM_RUN)
		return

	def getTSFRegs(self):
		while True :
			v3 = self.read16(self.B43_MMIO_TSF_3)
			v2 = self.read16(self.B43_MMIO_TSF_2)
			v1 = self.read16(self.B43_MMIO_TSF_1)
			v0 = self.read16(self.B43_MMIO_TSF_0)
			test3 = self.read16(self.B43_MMIO_TSF_3)
			test2 = self.read16(self.B43_MMIO_TSF_2)
			test1 = self.read16(self.B43_MMIO_TSF_1)
			if v3 == test3 and v2 == test2 and v1 == test1 :
				break
		return( (v3 << 48) + (v2 << 32) + (v1 << 16) + v0 )

class Disassembler:
	"""Disassembler for b43 firmware."""
	def __init__(self, binaryText, b43DasmOpts):
		input = NamedTemporaryFile()
		output = NamedTemporaryFile()

		input.write(binaryText)
		input.flush()
		#FIXME check b43-dasm errors
		os.system("b43-dasm %s %s %s" % (input.name, output.name, b43DasmOpts))

		self.asmText = output.read()

	def getAsm(self):
		"""Returns the assembly code."""
		return self.asmText

class Assembler:
	"""Assembler for b43 firmware."""
	def __init__(self, assemblyText, b43AsmOpts):
		input = NamedTemporaryFile()
		output = NamedTemporaryFile()

		input.write(assemblyText)
		input.flush()
		#FIXME check b43-asm errors
		os.system("b43-asm %s %s %s" % (input.name, output.name, b43AsmOpts))

		self.binaryText = output.read()

	def getBinary(self):
		"""Returns the binary code."""
		return self.binaryText

class TextPatcher:
	"""A textfile patcher that does not include any target context.
	This can be used to patch b43 firmware files."""

	class TextLine:
		def __init__(self, index, line):
			self.index = index
			self.line = line
			self.deleted = False

	def __init__(self, text, expected_md5sum):
		sum = hashlib.md5(text).hexdigest()
		if sum != expected_md5sum:
			print("Patcher: The text does not match the expected MD5 sum")
			print("Expected:   " + expected_md5sum)
			print("Calculated: " + sum)
			raise B43Exception
		text = text.splitlines()
		self.lines = []
		i = 0
		for line in text:
			self.lines.append(TextPatcher.TextLine(i, line))
			i += 1
		# Add an after-last dummy. Needed for the add-before logic
		lastDummy = TextPatcher.TextLine(i, "")
		lastDummy.deleted = True
		self.lines.append(lastDummy)

	def getText(self):
		"""This returns the current text."""
		textLines = []
		for l in self.lines:
			if not l.deleted:
				textLines.append(l.line)
		return "\n".join(textLines)

	def delLine(self, linenumber):
		"""Delete a line of text. The linenumber corresponds to the
		original unmodified text."""
		for l in self.lines:
			if l.index == linenumber:
				l.deleted = True
				return
		print("Patcher deleteLine: Did not find the line!")
		raise B43Exception

	def addText(self, beforeLineNumber, text):
		"""Add a text before the specified linenumber. The linenumber
		corresponds to the original unmodified text."""
		text = text.splitlines()
		index = 0
		for l in self.lines:
			if l.index == beforeLineNumber:
				break
			index += 1
		if index >= len(self.lines):
			print("Patcher addText: Did not find the line!")
			raise B43Exception
		for l in text:
			self.lines.insert(index, TextPatcher.TextLine(-1, l))
			index += 1

class B43SymbolicSpr:
	"""This class converts numeric SPR names into symbolic SPR names."""

	def __init__(self, header_file):
		"""The passed header_file parameter is a file path to the
		assembly file containing the symbolic SPR definitions."""
		try:
			defs = open(header_file).readlines()
		except IOError as e:
			print("B43SymbolicSpr: Could not read %s: %s" % (e.filename, e.strerror))
			B43Exception
		# Parse the definitions
		self.spr_names = { }
		r = re.compile(r"#define\s+(\w+)\s+(spr[a-fA-F0-9]+)")
		for line in defs:
			m = r.match(line)
			if not m:
				continue # unknown line
			name = m.group(1)
			offset = m.group(2)
			self.spr_names[offset.lower()] = name

	def get(self, spr):
		"""Get the symbolic name for an SPR. The spr parameter
		must be a string like "sprXXX", where XXX is a hex number."""
		try:
			spr = self.spr_names[spr.lower()]
		except KeyError:
			pass # Symbol not found. Return numeric name.
		return spr

	def getRaw(self, spr_hexnumber):
		"""Get the symbolic name for an SPR. The spr_hexnumber
		parameter is the hexadecimal number for the SPR."""
		return self.get("spr%03X" % spr_hexnumber)

class B43SymbolicShm:
	"""This class converts numeric SHM offsets into symbolic SHM names."""

	def __init__(self, header_file):
		"""The passed header_file parameter is a file path to the
		assembly file containing the symbolic SHM definitions."""
		try:
			defs = open(header_file).readlines()
		except IOError as e:
			print("B43SymbolicShm: Could not read %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		# Parse the definitions
		self.shm_names = { }
		in_abi_section = False
		r = re.compile(r"#define\s+(\w+)\s+SHM\((\w+)\).*")
		for line in defs:
			if line.startswith("/* BEGIN ABI"):
				in_abi_section = True
			if line.startswith("/* END ABI"):
				in_abi_section = False
			if not in_abi_section:
				continue # Only parse ABI definitions
			m = r.match(line)
			if not m:
				continue # unknown line
			name = m.group(1)
			offset = int(m.group(2), 16)
			offset /= 2
			self.shm_names[offset] = name

	def get(self, shm_wordoffset):
		"""Get the symbolic name for an SHM offset."""
		try:
			sym = self.shm_names[shm_wordoffset]
		except KeyError:
			# Symbol not found. Return numeric name.
			sym = "0x%03X" % shm_wordoffset
		return sym

class B43SymbolicCondition:
	"""This class converts numeric External Conditions into symbolic names."""

	def __init__(self, header_file):
		"""The passed header_file parameter is a file path to the
		assembly file containing the symbolic condition definitions."""
		try:
			defs = open(header_file).readlines()
		except IOError as e:
			print("B43SymbolicCondition: Could not read %s: %s" % (e.filename, e.strerror))
			raise B43Exception
		# Parse the definitions
		self.cond_names = { }
		r = re.compile(r"#define\s+(\w+)\s+EXTCOND\(\s*(\w+),\s*(\d+)\s*\).*")
		for line in defs:
			m = r.match(line)
			if not m:
				continue # unknown line
			name = m.group(1)
			register = m.group(2)
			bit = int(m.group(3))
			if register == "CONDREG_RX":
				register = 0
			elif register == "CONDREG_TX":
				register = 2
			elif register == "CONDREG_PHY":
				register = 3
			elif register == "CONDREG_4":
				register = 4
			elif register == "CONDREG_PSM":
				continue # No lookup table for this one
			elif register == "CONDREG_RCM":
				register = 6
			elif register == "CONDREG_7":
				register = 7
			else:
				continue # unknown register
			cond_number = bit | (register << 4)
			self.cond_names[cond_number] = name

	def get(self, cond_number):
		"""Get the symbolic name for an External Condition."""
		register = (cond_number >> 4) & 0x7
		bit = cond_number & 0xF
		eoi = ((cond_number & 0x80) != 0)
		cond_number &= ~0x80
		if register == 5: # PSM register
			return "COND_PSM(%d)" % bit
		try:
			sym = self.cond_names[cond_number]
		except KeyError:
			# Symbol not found. Return numeric name.
			sym = "0x%02X" % cond_number
		if eoi:
			sym = "EOI(%s)" % sym
		return sym

class B43AsmLine:
	def __init__(self, text):
		self.text = text

	def getLine(self):
		return self.text

	def __repr__(self):
		return self.getLine()

	def isInstruction(self):
		return False

class B43AsmInstruction(B43AsmLine):
	def __init__(self, opcode):
		self.setOpcode(opcode)
		self.clearOperands()

	def getOpcode(self):
		return self.opcode

	def setOpcode(self, opcode):
		self.opcode = opcode

	def clearOperands(self):
		self.operands = []

	def addOperand(self, operand):
		self.operands.append(operand)

	def getOperands(self):
		return self.operands

	def getLine(self):
		ret = "\t" + self.opcode
		if self.operands:
			ret += "\t"
		for op in self.operands:
			ret += op + ", "
		if self.operands:
			ret = ret[:-2]
		return ret

	def isInstruction(self):
		return True

class B43AsmParser:
	"""A simple B43 assembly code parser."""

	def __init__(self, asm_code):
		self.__parse_code(asm_code)

	def __parse_code(self, asm_code):
		self.codelines = []
		label = re.compile(r"^\s*\w+:\s*$")
		insn_0 = re.compile(r"^\s*([@\.\w]+)\s*$")
		insn_2 = re.compile(r"^\s*([@\.\w]+)\s+([@\[\],\w]+),\s*([@\[\],\w]+)\s*$")
		insn_3 = re.compile(r"^\s*([@\.\w]+)\s+([@\[\],\w]+),\s*([@\[\],\w]+),\s*([@\[\],\w]+)\s*$")
		insn_5 = re.compile(r"^\s*([@\.\w]+)\s+([@\[\],\w]+),\s*([@\[\],\w]+),\s*([@\[\],\w]+),\s*([@\[\],\w]+),\s*([@\[\],\w]+)\s*$")
		for line in asm_code.splitlines():
			m = label.match(line)
			if m: # Label:
				l = B43AsmLine(line)
				self.codelines.append(l)
				continue
			m = insn_0.match(line)
			if m: # No operands
				insn = B43AsmInstruction(m.group(1))
				self.codelines.append(insn)
				continue
			m = insn_2.match(line)
			if m: # Two operands
				insn = B43AsmInstruction(m.group(1))
				insn.addOperand(m.group(2))
				insn.addOperand(m.group(3))
				self.codelines.append(insn)
				continue
			m = insn_3.match(line)
			if m: # Three operands
				insn = B43AsmInstruction(m.group(1))
				insn.addOperand(m.group(2))
				insn.addOperand(m.group(3))
				insn.addOperand(m.group(4))
				self.codelines.append(insn)
				continue
			m = insn_5.match(line)
			if m: # Three operands
				insn = B43AsmInstruction(m.group(1))
				insn.addOperand(m.group(2))
				insn.addOperand(m.group(3))
				insn.addOperand(m.group(4))
				insn.addOperand(m.group(5))
				insn.addOperand(m.group(6))
				self.codelines.append(insn)
				continue
			# Unknown line
			l = B43AsmLine(line)
			self.codelines.append(l)

class B43Beautifier(B43AsmParser):
	"""A B43 assembly code beautifier."""

	def __init__(self, asm_code, headers_dir):
		"""asm_code is the assembly code. headers_dir is a full
		path to the directory containing the symbolic SPR,SHM,etc... definitions"""
		if headers_dir.endswith("/"):
			headers_dir = headers_dir[:-1]
		B43AsmParser.__init__(self, asm_code)
		self.symSpr = B43SymbolicSpr(headers_dir + "/spr.inc")
		self.symShm = B43SymbolicShm(headers_dir + "/shm.inc")
		self.symCond = B43SymbolicCondition(headers_dir + "/cond.inc")
		self.preamble = "#include \"%s/spr.inc\"\n" % headers_dir
		self.preamble += "#include \"%s/shm.inc\"\n" % headers_dir
		self.preamble += "#include \"%s/cond.inc\"\n" % headers_dir
		self.preamble += "\n"
		self.__process_code()

	def __process_code(self):
		spr_re = re.compile(r"^spr\w\w\w$")
		shm_re = re.compile(r"^\[(0x\w+)\]$")
		code = self.codelines
		for line in code:
			if not line.isInstruction():
				continue
			opcode = line.getOpcode()
			operands = line.getOperands()
			# Transform unconditional jump
			if opcode == "jext" and int(operands[0], 16) == 0x7F:
				label = operands[1]
				line.setOpcode("jmp")
				line.clearOperands()
				line.addOperand(label)
				continue
			# Transform external conditions
			if opcode == "jext" or opcode == "jnext":
				operands[0] = self.symCond.get(int(operands[0], 16))
				continue
			# Transform orx 7,8,imm,imm,target to mov
			if opcode == "orx" and \
			   int(operands[0], 16) == 7 and int(operands[1], 16) == 8 and\
			   operands[2].startswith("0x") and operands[3].startswith("0x"):
				value = int(operands[3], 16) & 0xFF
				value |= (int(operands[2], 16) & 0xFF) << 8
				target = operands[4]
				line.setOpcode("mov")
				line.clearOperands()
				line.addOperand("0x%X" % value)
				line.addOperand(target)
				opcode = line.getOpcode()
				operands = line.getOperands()
			for i in range(0, len(operands)):
				o = operands[i]
				# Transform SPR operands
				m = spr_re.match(o)
				if m:
					operands[i] = self.symSpr.get(o)
					continue
				# Transform SHM operands
				m = shm_re.match(o)
				if m:
					offset = int(m.group(1), 16)
					operands[i] = "[" + self.symShm.get(offset) + "]"
					continue

	def getAsm(self):
		"""Returns the beautified asm code."""
		ret = [ self.preamble ]
		for line in self.codelines:
			ret.append(str(line))
		return "\n".join(ret)
