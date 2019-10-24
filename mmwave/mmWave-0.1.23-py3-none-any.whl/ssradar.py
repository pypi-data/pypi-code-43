#Under development
import numpy as np
import struct
import serial

class SSR:
	magicWord =  [b'\x02',b'\x01',b'\x04',b'\x03',b'\x06',b'\x05',b'\x08',b'\x07',b'\0x99']
	tlvStatus = b""
	rangeProfile = b""
	version = "0.0"
	platform = "iwr1642" 
	
	def __init__(self,port):
		self.port = port
		print("***ssr init***")
		
	def ssr_test(self):
		print("*********SSR Called**********")
	
	def tlvRead(self):
		#print("---tlvRead---")
		idx = 0
		version = ""
		lstate = 'idle'
		sbuf = b""
		totalPackLen =0
		platform = ""
		frameNumber = 0
		timeCpuCycles = 0
		numDetectedObj = 0
		numTLVs = 0
		#*******Message TLV Header 1 *******
		mmWaveType1 = 0
		length1 = 0
		tlvNDO = 0
		xyzQFormat = 0
		#********Message TLV Header 2******
		mmWaveType2 = 0
		length2 = 0
		
		jb_doppler = 0
		jb_peakValue = 0
		jb_x = 0
		jb_y = 0
		tlvCnt = 0
		objCnt = 0
		objData = []
	
		while True:
			ch = self.port.read()
			#print(str(ch))
			if lstate == 'idle':
			#print("state:" + lstate)
				if ch == self.magicWord[idx]:
					#print("*** magicWord:"+ "{:02x}".format(ord(ch)))
					#GPIO.output(21, True)
					idx += 1
					if idx == 8:
						idx = 0
						lstate = 'header'
						rangeProfile = b""
						tlvStatus = b""	
						sbuf = b""
				else:
					idx = 0
					rangeProfile = b""
					tlvStatus = b""	
					return (0 , [])
		
			elif lstate == 'header':
				sbuf += ch
				idx += 1
				#print(str(ch))
				if idx == 44:
					# print("------header-----")
					# print(":".join("{:02x}".format(c) for c in sbuf))
					# print("------header end -----")
				
					# [header - Magicword] + [Message TLV header] 
					try:   		  
						self.version , totalPackLen, self.platform , frameNumber, timeCpuCycles, numDetectedObj, numTLVs, subFrameNumber, mmWaveType1, length1 , tlvNDO, xyzQFormat = struct.unpack('10Ihh', sbuf) 
					except:
						print("Improper TLV structure found: ")
						return (0, [])
						break
					
					#print("********32**************") 
					#print("PID:\t%d "%(frameNumber))
					#print("Version:\t%x "%(version))
					#print("TotalPackLen:\t%d "%(totalPackLen))
					#print("Platform:\t%X "%(platform))
					#print("FrameNumber:\t%X "%(frameNumber))
					#print("timeCpuCycles:\t%d "%(timeCpuCycles))
					print("---")
					#print("numDetectedObj:\t%d "%(numDetectedObj))
					#print("numTLVs:\t%d "%(numTLVs))
					#print("subFrameNumber:\t%d "%(subFrameNumber))
				
					if numTLVs == 0 or tlvNDO > 200:
						lstate = 'idle'
						return (0, [])
				
					#[Message TLV header] = 8 bytes
					#print("mmWave Type:\t%d "%(mmWaveType1)) #4 bytes
					#print("Data 1 Len:\t%d "%(length1))      #4 bytes
					#print("tlvNDO:\t%d "%(tlvNDO))           #2 bytes
					#print("xyzQFormat:\t%d "%(xyzQFormat))   #2 bytes
				
				
					sbuf = b""
					idx = 0
					lstate =  'tlv0Data'
					tlvCnt = 0
					objCnt = 0
					objData = []
					if length1 > totalPackLen:
						length1 = totalPackLen - 52   #44 + 8(magic word)
						print("length1:" + str(length1))
					
				elif idx > 44:
					idx = 0
					lstate = 'idle'
				
			elif lstate == 'tlv0Data':
				tlvCnt = 1
				idx += 1
				sbuf += ch
				#print(ch)
				if idx == 8:
					#print(":".join("{:02x}".format(c) for c in sbuf))
					dev = 2**7
					try:
						jb_doppler,jb_peakValue,jb_x,jb_y = struct.unpack('hHhh' , sbuf)
						objData.append((objCnt,float(jb_doppler),float(jb_peakValue),float(jb_x)/dev,float(jb_y)/dev))
					except:
						print("Improper TLV structure found:")
						return (0,[])
					
					lstate = 'tlv0Data'
				
					#print("data(%d):\t%f : %f : %f : %f"%(objCnt,float(jb_doppler),float(jb_peakValue)/dev,float(jb_x)/dev,float(jb_y)/dev))
					sbuf = b""
					idx = 0
					objCnt += 1
					#print("objCnt:" + str(objCnt))
					if objCnt >= tlvNDO:
						#print("objCnt > tlvNDO:") 
						lstate = 'idle'
						objCnt = 0
						#from here
						return (1,objData)
					
					
				elif idx > length1:
					print("idx > length1")
					idx = 0
					lstate = 'idle'
				
				
			#
			#following data is not use		
			#
			elif lstate == 'mmWaveType2+len':
				sbuf += ch
				idx += 1
				if idx == 8:
					idx = 0
					mmWaveType2 , length2 = struct.unpack('2I',sbuf)
					if length2 > 288:
						length2 = 288
						lstate = 'data2'
						rangeProfile = b""
						#[Message TLV header] = 8 bytes
						#print("mmWave Type 2:\t%d "%(mmWaveType2))
						#print("Data 2 Len:\t%d "%(length2))	  
				elif idx > 8:
					idx = 0
					lstste = 'idle'
				
			elif lstate == 'data2':
				rangeProfile += ch
				idx += 1
				if idx == length2:
					idx = 0 
					#print("---------rangeProfile:" + str(len(rangeProfile)))
					#print ":".join("{:02x}".format(c) for c in rangeProfile)
					#GPIO.output(21, False)
					return (tlvStatus , rangeProfile)
			elif idx > length2:
				idx = 0
				lstate = 'idle'
	
	
	def checkMagicWord(rcvData):
		idx = 0
		rv =""
		for c in rcvData:
			if c == magicWord[idx] and idx < len(magicWord):
				idx += 1
				print(c)
			else:
				return ""
		
			if idx == len(magicWord):  	   
				rv += c
				if ch == '\r' or ch == '':
					return rv

