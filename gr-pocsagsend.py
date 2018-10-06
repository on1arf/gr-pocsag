"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!


"""
#gr-pocsag: a gnuradio embedded python block for sending pocsag messages
#-----------------------------------------------------------------------
#
#
#This is the alpha test release of gr-pocsag, a embedded python block for generating and
#sending pocsag message.
#
#The gnu-radio companion example uses a hackRF to send a pocsag-message on 433.900 Mhz.
#
#
#The block generates the bitpattern for a POCSAG-message, broadcasts it once and then going into a loop
#to shut down the transmitter module of the HackRF.
#
#
#The python code itself is located inside the "pocsag generator" epy_block and as a seperate file "gr-pocsagsend.py".
#
#
# (C) Kristoff Bonne, ON1ARF
# GPL v3
#
#Release-information:
#Version: 0.0.1 (20180826)
#Version: 0.0.2 (20180828)
#Version: 0.0.3 (20181006): correction idle pattern and changing "20 bits padding" pattern
#
# 73s . kristoff - ON1ARF


import numpy as np
from gnuradio import gr

from bitstring import BitArray

import time



class pocsagsender(gr.sync_block):
	def __CalculateCRCandParity(self,datatype,data):
		cw=data<<11 

		# make leftmost bit "1" for datatype 1 (text)
		if datatype == 1:
			cw |= 0x80000000
		#end if

		local_cw=cw

		for i in range(21):
			if (cw & 0x80000000) > 0:
				cw ^= 0xED200000
			#end if
			cw <<= 1
		#end for

		local_cw |= (cw >> 21)


		parity=0
		cw=local_cw
		for i in range(32):
			if (cw & 0x80000000) > 0:
				parity += 1
			#end if
			cw <<= 1
		#end for

		# make even parity
		local_cw += (parity % 2)

		return(local_cw)
	# end Calculate CRC and Pairy


	def __createpocsagmsg(self,address,source,txt):

		# checking input
		if not (0 < address <= 0x1fffff):
			raise ValueError(address)
		#end if

		if not (0 <= source <= 3):
			raise ValueError(source)
		#nd if


		if len(txt) == 0:
			raise ValueError(txt)
		#end if


		if len(txt) >= 40:
			txt=txt[:39]
			print("Warning, text truncated to 39 characters: {txt}".format(txt=txt))
		#end if

		# init pocsag message
		# init data
		# 2 batches
		# 1 batch = sync codeword + 8 frames
		# 1 frame = 1 codeword

		syncpattern = 0xAAAAAAAA
		synccodeword = 0x7cd215d8

		idlepattern  = 0x7ac9c197

		# init all codewords with idle pattern: 2 batches = 16 frames = 32 codewords
		codeword = [idlepattern for i in range(32)]


		# part 1: address + source 

		# parse address and source
		addressline=address>>3

		# add address-source
		addressline<<=2
		addressline += source
		# the message starts at the frame address determined by the last 3 bits of the address
		cwnum = ((address % 8) << 1) # codeword number

		codeword[cwnum]=self.__CalculateCRCandParity(datatype = 0, data = addressline)


		# part 2: text
        
		# 2.1 convert text into int, also add EOT char
		ts=[ord(c) for c in txt] + [0x04] 

		# 2.2 make sure all characers are 7 bit
		ts=list(map(lambda x: x%128, ts))

		# 2.3 create one big list of bits
		textbits=''

		for c in ts:
			# BitArray(uint=c,length=7).bin to convert character to 7-character bit-string)
			# note, for transmission, the bit-order must be reversed
			charbits = BitArray(uint=c,length=7)
			# reverse order of bits
			charbits.reverse()

			# add to total string
			textbits += charbits.bin
		#end for

		nbits=len(textbits)

		# 2.4 make the list of bits  a multiple of 20 bits
		bitstoadd=20-(nbits % 20)

		if bitstoadd == 20:
			bitstoadd = 0
		#end if
		bitstoadd_rest = bitstoadd%2
		bitstoadd_2bit = bitstoadd >> 1
		textbits += '01' * bitstoadd_2bit
		if bitstoadd_rest == 1:
			textbits += '0'
		#end if


		# 2.5 for every block of 20 bits, calculate crc and partity, and add to codeword
		ncw = len(textbits)/20 # number of codewords

		startbit=0
		stopbit=20 # (actually, the 19th bit)
		for i in range(ncw):
			thiscw=textbits[startbit:stopbit]
			thiscw_i=int(thiscw,2) # convert list of bits to int

			#move up all pointers
			startbit=stopbit # stopbit is startbit + 20
			stopbit += 20

			#codeword pointer
			cwnum += 1

			# calculate CRC for a text block (datatype = 1)
			codeword[cwnum]=self.__CalculateCRCandParity(datatype = 1, data = thiscw_i)
		#end for (number of 


		# done

		# now create complete pocsag message
		# sync pattern
		ret = [syncpattern for i in range(18)]
        
		# add sync codeword of 1st batch
		ret.append(synccodeword)

		# add frames 0 to 7 (i.e. codewords 0 to 15)
		ret += [codeword[n] for n in range(16)]


		
		# create add 2nd batch if the text has spilled into the 2nd batch
		if cwnum >=  16:
			# long message, 2 batches
			nbatch=2

			# add sync codeword
			ret.append(synccodeword)
        
			# and add frames 8 to 15 (i.e. codewords 16 to 31)
			ret += [codeword[n] for n in range(16,32)]
		else:
			# short message, 1 batch
			nbatch=1

		#end else - ifif


		return((nbatch,ret))

	# end "createpocsagmsg"


	def __init__(self, number = 2060073, source = 0,  sleeptime= 5, text="ON1ARF pocsag Python gnuradio"):  # only default arguments here
		gr.sync_block.__init__(
			self,
			name='pocsag generator',
			in_sig=[],
			out_sig=[np.int8]
		)


		self.set_output_multiple(640)
			# pocsag messages are either 1 batch (35 codeword = 120 octets), or 2 batches (52 codewords = 208 octets)
			# make the stream a little bit longer to fit a multiple of 20 codewords
			# pocsag message of 1 batch -> add 5 cw -> 40 (= 20 * 2) codewords
			# pocsag message of 2 batches -> add 8 cw -> 60 (=20 *3) codewords
			# 20 cw = 80 octets = 640 bits

		self.state = 0
		self.sleeptime = sleeptime
		self.number= int(number)
		self.source = int(source)


		nbatch,psmsg=self.__createpocsagmsg(number,source,text)

		# for a short message (nbtach=1), add 5 octest = 40 bits
		# for a long message (nbatch=2), add 8 octets = 64 bits

		if nbatch == 1:
			self.pocsagmsg=[0 for i in range(20)]
		elif nbatch == 2:
			self.pocsagmsg=[0 for i in range(32)]
		else:
			raise ValueError(nbatch)
		#end if
			

		for thismsg in psmsg:
			for c in BitArray(uint=thismsg,length=32).bin:
				self.pocsagmsg.append(1 if c == '1' else -1)
		#end for

		# now add tail (all 0)
		if nbatch == 1:
			self.pocsagmsg+=[0 for i in range(20)]
		elif nbatch == 2:
			self.pocsagmsg+=[0 for i in range(32)]
		else:
			raise ValueError(nbatch)
		#end if

		self.msglen=len(self.pocsagmsg)

	#end __init__

	#def forecast(self, noutput_items, ninput_items_required):
	#	#setup size of input_items[i] for work call
	#	for i in range(len(ninput_items_required)):
	#		ninput_items_required[i] = noutput_items

	def work(self, input_items, output_items):

		if self.state == 0:
			# state 0 -> send pocsag message 

			output_items[0][:self.msglen]=np.array(self.pocsagmsg, dtype=np.int8)

			self.state = 1 # after this, go to sleep 
			return self.msglen
		#end if

		# state 1: sleep
		time.sleep(self.sleeptime)

		# then go back to state 0 (transmit)
		self.state = 0

		return -1 # return without any data
	#end work
# end class "pocsagsender"
