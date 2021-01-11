#!/usr/bin//python3
# -*- coding: utf-8 -*-

#########################################################
#   Program pro ovladani osciloskopu UT2XXX             #
#   Basic program for DSO controll			#
#                                                       #
#   Ing. Košan Tomáš, prosinec 2008                     #
#                                                       #
#   Licence: GNU GPL v2                                 #
#########################################################


# VID and PID of osciloscope
# VID a PID zarizeni
PID = [2098]
VID = [22102] 

from ut2XXX.ut2XXX_definitions import *
import logging

import usb, time, sys, os
from io import StringIO,BytesIO

# main class, encapsulates all USB communication
class UNI_T_DSO:

	# init
	def __init__(self):
		
		# init of basic data structures
		self.ch1_data = {}
		self.ch2_data = {}
		self.data_raw = ""
		self.status = {}
		
		# init status
		self.status["far_mode"]  = False
		self.status["locked"]    = False 
		self.status["info_data"] = []
		
		# init ch1 data
		self.ch1_data["samples"] = []
		self.ch1_data["V_div"]   = 0
		self.ch1_data["s_div"]   = 0
		self.ch1_data["couple"]  =""
		self.ch1_data["active"]  = False
		self.ch1_data["x_offset"]  = 0
		self.ch1_data["Bw_limit"] = False
		self.ch1_data["header"] = []
		self.ch1_data["probe"] = 0
		self.ch1_data["probe_index"] = 0
		self.ch1_data["changed"] = False
		self.ch1_data["s_div_index"] = 0
		self.ch1_data["inverted"] = False
		self.ch1_data["y_offset"] = 125
		self.ch1_data["y_poz"] = 3803
		
		# init ch1 data
		self.ch2_data["samples"] = []
		self.ch2_data["V_div"]   = 0
		self.ch2_data["s_div"]   = 0
		self.ch2_data["couple"]  =""
		self.ch2_data["active"]  = False
		self.ch2_data["x_offset"]  = 0
		self.ch2_data["Bw_limit"] = False
		self.ch2_data["header"] = []
		self.ch2_data["probe"] = 0
		self.ch2_data["probe_index"] = 0
		self.ch2_data["changed"] = False
		self.ch2_data["s_div_index"] = 0
		self.ch2_data["inverted"] = False
		self.ch2_data["y_offset"] = 125
		self.ch2_data["y_poz"] = 3803
				
		self.data_old = ()
		self.pixmap_data = ()
		
		self.error_message = ""
		
		self.init()
	
	# find DSO and initiate it
	def init(self):	
		# load VID and PIDS from external file	
		self.load_vid_pid()
		self.device = None
		self.interface_id = 0
		self.config_id = 1
		self.endpoints = []
		# try to find devicecd
		self.find_device()
		# device not found
		if not self.device:
			logging.error("Error finding device. Exiting.")
			self.is_present = False
		# Yes, weve got a DSO connected 
		else:
			logging.info ("Dbg: Device is presented")
			self.is_present = True
			self.handle = self.device.open()
			logging.info ("Dbg: device opened")
			
			#self.product = self.handle.getString(self.device.iProduct, 50)
			#print ("Dbg: getting product ID")
			#usb.util.get_string(handle, dev.iManufacturer)
			#self.manufacturer = self.handle.getString(self.device.iManufacturer, 50)
			#print ("Dbg: getting manufacturer")
			#self.handle.setConfiguration(self.config_id)
			#print ("Dbg: device configured")
			#self.handle.claimInterface(0)
			#logging.info ("Dbg: interface claimed")
			# init device
			self.init_device()
		
		self.data = None
	
	# loads VIDs and PIDs from external file - vid_pid.txt
	def load_vid_pid(self):
		# file should be in our install dir
		self.path = os.path.dirname(sys.argv[0])
		try:
			# load VID and PID
			for line in open(os.path.join(self.path,"./vid_pid.txt")):
				# ignore comment
				if len(line.split('#')[0])>0:
					line = line.replace('\r','').replace('\n','')
					VID.append(int(line.split('#')[0].split(',')[0]))
					PID.append(int(line.split('#')[0].split(',')[1]))
		except Exception as s:
			logging.warn("Wrn: Exception in reading VID/PID -> %s",s)
		# report
		logging.info ("Loaded VID/PIDS are:")
		logging.info ("VIDs -> %s",VID)
		logging.info ("PIDs -> %s",PID)

	# try to find proper USB device and get config
	def find_device(self):
		busses = usb.busses()
		for bus in busses:
			devices = bus.devices
			for dev in devices:
				# is device in our PID and VID lists ?
				if dev.idProduct in PID and dev.idVendor in VID:
					logging.info ("Found UNI-T DSO on USB:")
					#print "  iManuf. :",dev.iManufacturer
					logging.info ("idVendor: %s",dev.idVendor)
					logging.info ("idProduct: %s",dev.idProduct)
					#return dev
					self.device = dev
					#print dev
					for config in dev.configurations:
						for intf in config.interfaces:
							#print ("    Interface:",intf[0].interfaceNumber)
							for alt in intf:
								logging.info ("    Alternate Setting: %s",alt.alternateSetting)
								logging.info ("      Interface class: %s",alt.interfaceClass)
								logging.info ("      Interface sub class: %s",alt.interfaceSubClass)
								logging.info ("      Interface protocol: %s",alt.interfaceProtocol)
								# find all endpoints
								for ep in alt.endpoints:
									self.endpoints.append(ep.address)
									logging.info ("      Endpoint: %s",hex(ep.address))
									logging.info ("        Type: %s",ep.type)
									logging.info ("        Max packet size: %d",ep.maxPacketSize)
									logging.info ("        Interval: %d",ep.interval)
					
  	# enters far mode - it means all control on osciloscope is blocked
	def enter_far_mode(self):
		ans = False
		try:
			self.handle.controlMsg(0x42,0xb1,None,value=0xf0)
			ans = True
		except Exception as s:
			self.error_message = s
			logging.error ("Error entering remote control mode.")
		else:
			self.status["far_mode"] = True	
		return ans
		
	# leaves far mode - unblocks local control of osciloscope
	def leave_far_mode(self):
		ans = False
		try:
			self.handle.controlMsg(0x42,0xb1,None,value=0xf1)
			ans = True
		except Exception as s:
			self.error_message = s
			logging.error("Error leaving remote control mode.")
		else:
			self.status["far_mode"] = False			
		return ans	
	
	# returns some values, but I don't know what they means ... 
	def get_info_from_device(self):		
		# asi nastaveni jednotlivych ovl. prvku
		# maybe state of control
		ans = False
		try:
			self.handle.controlMsg(0x42,0xb1,None, value=0x2c)
			self.handle.controlMsg(0x00,0xb2,None)
			self.status["info_data"] = self.handle.controlMsg(0xc2,0xb2, 8)
			ans = True
		except Exception as s:
			logging.error("Error in get_info_from_device: %s",s)
			self.error_message = s	
		return ans	
	
	# basic function for send some message to DSO
	def send_message(self, message):
		ans = False
		try:	
			self.handle.controlMsg(0x42,0xb1,None,value=message)
			time.sleep(0.05)
			ans = True
		except Exception as ex:
			logging.error("Error in send_message: %s",ex)
		return ans
	
	# receive data from DSO, returns 1024 byte of data, some description in doc directory
	def get_data(self):
		for i in range(0,5):
			self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xe1)	
			time.sleep(0.03)	
			self.handle.controlMsg(0x42,0xb0,None,index=2, value=0x01)	
			#time.sleep(0.02)	
			try:
				data = self.handle.bulkRead(130,1024,60)
			except Exception as ex:
				logging.warning("Exception: %s",ex)
				data = self.data
			else:
				break
			#time.sleep(0.01)		
			self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)		
		return data
		
	def get_parameters(self):
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xe3)	
		time.sleep(0.05)	
		self.handle.controlMsg(0x42,0xb0,None)	
		try:
			data = self.handle.bulkRead(0x82,512,500)
		except:
			logging.error("Exception, sending old data.")
			self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)
			data = self.data		
		
		self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)
		return data	

	#ping DSO
	def ping(self):
		self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)	
		time.sleep(0.02)	
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		time.sleep(0.02)	

	
	def close(self):
		logging.info ("Closing, bye.")
		self.leave_far_mode()
		self.handle.releaseInterface()

				
	def init_device(self):
		try:
			self.handle.controlMsg(0xc2,0xb2,8,index=4, value=0x08, timeout=300)	
			time.sleep(0.02)	
		except:
			pass
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0x2c)	
		time.sleep(0.02)	
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xdc)	
		time.sleep(0.02)	
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		time.sleep(0.02)	
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		time.sleep(0.02)
		self.leave_far_mode()	
		
	
	def print_status(self):
		logging.info ("Device: %s",self.product[0])
		logging.info ("Manufacturer: %s", self.manufacturer)
		self.get_waveform()
		logging.info ("------------------------------")
		if self.ch1_data["active"]:
			logging.info ("Inf: Chanel 1: ON")
		else:
			logging.info ("Inf: Chanel 1: OFF") 
		logging.info ("X range: %d V/div", self.ch1_data["V_div"])
		logging.info ("Coupling:%d ", self.ch1_data["couple"])
		logging.info ("Y range: %d s/div", self.ch1_data["s_div"])
		
		if self.ch2_data["active"]:
			logging.info ("Chanel 2: ON")
		else:
			logging.info ("Chanel 2: OFF") 
		logging.info ("X range: %d V/dic", self.ch2_data["V_div"])
		logging.info ("Coupling:%d", self.ch2_data["couple"])
		logging.info ("Y range: %d s/div", self.ch2_data["s_div"])
		

	def parse_waveform(self, filename):
		self.get_waveform(open(filename).readlines())

	# get samples from DSO
	def get_waveform(self, extern_data = None):
		# if not extern data load form DSO
		data = None
		if not extern_data:
			data = self.get_data()
		else:
			data = extern_data
		#print "Data length is:",len(data)
		
		# check for proper length of data packet	
		if not data == None and len(data) >= 1024:
			
			self.data_raw = data
			
			if not self.ch1_data["header"] == data[0:32]:
				self.ch1_data["changed"] = True
				
				# just for quick debug
				#if len(self.ch1_data["header"]) == 32:
				#	for i in range(0,32):
				#		if not self.ch1_data["header"][i] == data[i]:
				#			print ("Change:",i,"value prev./now",self.ch1_data["header"][i],data[i])
			else:
				self.ch1_data["changed"] = False
				
			if not self.ch2_data["header"] == data[32:64]:
				self.ch2_data["changed"] = True
			else:
				self.ch2_data["changed"] = False
			
			self.ch1_data["header"] = data[0:32]
			self.ch2_data["header"] = data[32:64]
			
			# compute V/div for each chanel
			self.ch1_data["V_div"] = Y_RANGE[data[Y_SENSE_CH1]]*(10**(data[Y_PROBE_CH1]))
			self.ch1_data["V_div_index"] = data[Y_SENSE_CH1]
			self.ch2_data["V_div"] = Y_RANGE[data[Y_SENSE_CH2]]*(10**(data[Y_PROBE_CH2]))
			self.ch2_data["V_div_index"] = data[Y_SENSE_CH2]
			
			# probe
			self.ch1_data["probe"] = 10**(data[Y_PROBE_CH1])
			self.ch1_data["probe_index"] = data[Y_PROBE_CH1]
			self.ch2_data["probe"] = 10**(data[Y_PROBE_CH2])
			self.ch2_data["probe_index"] = data[Y_PROBE_CH2]
			
			# check for coupling
			self.ch1_data["couple"] = COUPLING[data[COUPLING_CH1]]
			self.ch2_data["couple"] = COUPLING[data[COUPLING_CH2]]
			self.ch1_data["couple_index"] = data[COUPLING_CH1]
			self.ch2_data["couple_index"] = data[COUPLING_CH2]
			
			# save samples data to buffers
			if len(data) == 1024:
				self.ch1_data["samples"] = data[516:766]
				self.ch2_data["samples"] = data[770:1020]
			
			elif len(data) == 2560: 
				self.ch1_data["samples"] = data[516:1266]
				self.ch2_data["samples"] = data[1520:2270]
			
			else:
				logging.error("Unexcepted length of data sample, no data decoded then.")
				
			# compute t/div
			self.ch1_data["s_div"] = X_RANGE[data[X_SCALE_CH1]]
			self.ch1_data["s_div_index"] = data[X_SCALE_CH1]
			self.ch2_data["s_div"] = X_RANGE[data[X_SCALE_CH2]]
			self.ch2_data["s_div_index"] = data[X_SCALE_CH2]
			
			# check status of channels
			self.ch1_data["active"] = bool(data[CHANNEL_STATE] & 0x01)
			self.ch2_data["active"] = bool(data[CHANNEL_STATE] & 0x02)
			
			# x offset
			self.ch1_data["y_offset"] = 0x7e - data[Y_POS_CH1]
			self.ch2_data["y_offset"] = 0x7e - data[Y_POS_CH2]
			
			self.ch1_data["Bw_limit"] = bool(data[BW_LIMIT_CH1])
			self.ch2_data["Bw_limit"] = bool(data[BW_LIMIT_CH2])
			
			self.ch1_data["inverted"] = bool(data[INVERTED_CH1])
			self.ch2_data["inverted"] = bool(data[INVERTED_CH2])
			
			self.ch1_data["x_offset"] = data[X_CURSOR_CH1]
			self.ch2_data["x_offset"] = data[X_CURSOR_CH2]
			
			self.ch1_data["x_poz"] = (data[X_POS_MSB_CH1] << 8) + data[X_POS_LSB_CH1]
			self.ch2_data["x_poz"] = (data[X_POS_MSB_CH2] << 8) + data[X_POS_LSB_CH2]
		
		else:
			if data == None:
				count = 0
			else:
				count = len(data)
			logging.warning("%s Data buffer error: %d",time.time(), count)
		
	def test_screenshot(self):
		self.get_screenshot()
		for i in range(0,len(self.data)):
			try:
				if self.data_old[i] != self.data[i]:
					logging.info("Changed to %d", i) 
			except:
				pass
		self.data_old = self.data
		
	def get_screenshot(self, filename=""):
		self.data = ()
		ts = time.time()
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xe2)	
		time.sleep(0.05)	
		self.handle.controlMsg(0x42,0xb0,None,index=2, value=0x26)	
		#time.sleep(0.01)
		self.pixmap_data = self.handle.bulkRead(130,38912,1000)
		logging.info ("Processing time: %s",time.time() - ts)
		logging.info ("Loaded:%d bytes",len(self.pixmap_data))
		
		pixel_data = []
		
		if len(self.pixmap_data) == 38912:
			pixel_data = self.write_pixmap(filename)
		else:
			logging.info("Too few data for screenshot.")
		return pixel_data
		
	# write binary ppm bitmap created from screenshot data from DSO
	def write_pixmap(self, filename=""):
		
		# fake file
		bitmap_data = BytesIO()
		
		# size of bitmap
		width=320; height=240
		#use 'P3' for ascii, 'P6' for binary
		try:
			if filename == "":
				ppmfile=open('testimage.ppm','wb')
			else:
				ppmfile=open(filename,'wb')
			
			header = ("P6\n {} {}\n {}\n").format(width ,height,255)	
			bitmap_data.write(header.encode('utf-8')) 
			
			# working with 2 bytes in one time
			for index in range(0,len(self.pixmap_data),2):
				
				# pixmapdata have exchanged even and odd bytes
				# we correct it with order of writing
				# another problem is, that one byte include TWO pixels data
				# we must shift it and then decode which color that value means
				
				color = self.pixmap_data[index+1]
				color2 = ((color) & 0x0F)
				color1 = ((color) & 0xF0) >> 4
				
				color = self.pixmap_data[index]
				color4 = ((color) & 0x0F)
				color3 = ((color) & 0xF0) >> 4
				
				bitmap_data.write(self.convert_to_color(color1))
				bitmap_data.write(self.convert_to_color(color2))
				bitmap_data.write(self.convert_to_color(color3))
				bitmap_data.write(self.convert_to_color(color4))
		
		except Exception as ex:
			logging.info("Exception in write_pixmap: %s -Y %s",filename,ex)
		
		finally:
			s = bitmap_data.getvalue()
			ppmfile.write(s)
			bitmap_data.close()
			ppmfile.close()
		return s
	
	# we need to convert raw data to RGB color tuple
	def convert_to_color(self, color):
		
		# black
		if  color == 0x00:
			return (b'\x00\x00\x00')
		# dark grey
		elif color == 0x01:
			return (b'\x00\x00\x40')
		# dark blue
		elif color == 0x03:
			return (b'\x05\x04\xaa')
		# lighter blue
		elif color == 0x05:
			return (b'\x00\x00\xC0')
		# red
		elif color == 0x06:
			return (b'\x00\xF4\x00')
		#
		elif color == 0x07:
			return (b'\x80\x20\x00')
		# grid color - cyan
		elif color == 0x08:
			return (b'\x00\x7D\x7D')
		# dark red
		elif color == 0x09:
			return (b'\x80\x20\x00')
		
		elif color == 0x0A:
			return (b'\x7D\x7D\x7d')
		# darker blue
		elif color == 0x0b:
			return (b'\x00\x00\x80')
		# cyan
		elif color == 0x0C:
			return (b'\x00\xC0\xC0')
		# yellow
		elif color == 0x0D:
			return (b'\xFF\xFF\x00')
		# red
		elif color == 0x0E:
			return (b'\xE0\x20\x00')
		# white
		elif color == 0x0F:
			return (b'\xFF\xFF\xFF')
		else:
			logging.info ("Inf: Unsuported color: %d", color)
			return (b'\xFF\xFF\xFF')	

	# test changes in data from DSO
	def test_parameters(self):
		data = dso.get_parameters()
		if self.data == None:
			self.data = data
		for i in range(0,150):
			if not self.data[i] == data[i]:
				logging.info("Change at %d value prev./now %d / %d",i,self.data[i],data[i])
				
		self.data = data

# for testing functions
if __name__ == '__main__':

	dso = UNI_T_DSO()
	if dso.is_present:
		while raw_input("q = konec / quit") != "q":
			dso.test_parameters()
			#print "Info:",dso.get_info_from_device(), dso.status
			#print "Param:", dso.get_parameters()
		
		dso.leave_far_mode()
		dso.ping()
		
		dso.close()
	else:
		logging.error("Device was not recognized or found.")
