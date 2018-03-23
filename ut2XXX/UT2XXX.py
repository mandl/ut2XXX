#!/usr/bin//python
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

from ut2XXX_definitions import *

import usb, time, StringIO, sys, os

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
		# try to find device
		self.find_device()
		# device not found
		if not self.device:
			print "Err: Error finding device. Exiting."
			self.is_present = False
		# Yes, weve got a DSO connected 
		else:
			print "Dbg: Device is presented"
			self.is_present = True
			self.handle = self.device.open()
			print "Dbg: device opened"
			#self.product = self.handle.getString(self.device.iProduct, 50)
			print "Dbg: getting product ID"
			#self.manufacturer = self.handle.getString(self.device.iManufacturer, 50)
			print "Dbg: getting manufacturer"
			#self.handle.setConfiguration(self.config_id)
			print "Dbg: device configured"
			#self.handle.claimInterface(self.interface_id)
			print "Dbg: interface claimed"
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
		except Exception, (s):
			print "Wrn: Exception in reading VID/PID ->",s
		# report
		print "Inf: Loaded VID/PIDS are:"
		print "Inf: VIDs -> ",VID
		print "Inf: PIDs -> ",PID


	# try to find proper USB device and get config
	def find_device(self):
	
		busses = usb.busses()
		
		for bus in busses:
			devices = bus.devices
			for dev in devices:
				# is device in our PID and VID lists ?
				if dev.idProduct in PID and dev.idVendor in VID:
					print "Inf: Found UNI-T DSO on USB:"
					#print "  iManuf. :",dev.iManufacturer
					print "Inf:  idVendor:",dev.idVendor
					print "Inf:  idProduct:",dev.idProduct
					#return dev
					self.device = dev
					#print dev
					for config in dev.configurations:
						for intf in config.interfaces:
							#print "    Interface:",intf[0].interfaceNumber
							for alt in intf:
								print "    Alternate Setting:",alt.alternateSetting
								print "      Interface class:",alt.interfaceClass
								print "      Interface sub class:",alt.interfaceSubClass
								print "      Interface protocol:",alt.interfaceProtocol
								# find all endpoints
								for ep in alt.endpoints:
									self.endpoints.append(ep.address)
									print "      Endpoint:",hex(ep.address)
									print "        Type:",ep.type
									print "        Max packet size:",ep.maxPacketSize
									print "        Interval:",ep.interval
					
  	# enters far mode - it means all control on osciloscope is blocked
	def enter_far_mode(self):
		ans = False
		try:
			self.handle.controlMsg(0x42,0xb1,None,value=0xf0)
			ans = True
		except Exception, (s):
			self.error_message = s
			print "Err: Error entering remote control mode."
		else:
			self.status["far_mode"] = True	
		return ans
		
	# leaves far mode - unblocks local control of osciloscope
	def leave_far_mode(self):
		ans = False
		try:
			self.handle.controlMsg(0x42,0xb1,None,value=0xf1)
			ans = True
		except Exception, (s):
			self.error_message = s
			print "Err: Error leaving remote control mode."
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
		except Exception, (s):
			print "Err: Error in get_info_from_device:",s
			self.error_message = s	
		return ans	
	
	# basic function for send some message to DSO
	def send_message(self, message):
		ans = False
		try:	
			self.handle.controlMsg(0x42,0xb1,None,value=message)
			time.sleep(0.05)
			ans = True
		except Exception, (s):
			print "Err: Error in send_message:",s
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
			except:
				#print "Exception:",s
				data = self.data
			else:
				break
			#time.sleep(0.01)		
			self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)	
#		time.sleep(0.01)	
#		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		return data
		
	def get_parameters(self):
		
		#self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)	
		#time.sleep(0.02)	
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)	
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)	
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)	
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)	
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)	
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xe3)	
		time.sleep(0.05)	
		self.handle.controlMsg(0x42,0xb0,None)	
		try:
			data = self.handle.bulkRead(0x82,512,500)
		except:
			print "Err: Exception, sending old data."
			self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)
			data = self.data		
		
		self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)
		return data	

	def ping(self):
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.01)	
		self.handle.controlMsg(0x42,0xb0,None,index=0, value=0xdc)	
		time.sleep(0.02)	
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		time.sleep(0.02)	

	
	def close(self):
		print "Inf: Closing, bye."
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
		print "Inf: Device:",self.product[0]
		print "Inf: Manufacturer:", self.manufacturer
		self.get_waveform()
		print "Inf: ------------------------------"
		if self.ch1_data["active"]:
			print "Inf: Chanel 1: ON"
		else:
			print "Inf: Chanel 1: OFF" 
		print "Inf: X range: ", self.ch1_data["V_div"],"V/div"
		print "Inf: Coupling:", self.ch1_data["couple"]
		print "Inf: Y range: ", self.ch1_data["s_div"], "s/div"
		
		if self.ch2_data["active"]:
			print "Inf: Chanel 2: ON"
		else:
			print "Inf: Chanel 2: OFF" 
		print "Inf: X range: ", self.ch2_data["V_div"],"V/div"
		print "Inf: Coupling:", self.ch2_data["couple"]
		print "Inf: Y range: ", self.ch2_data["s_div"], "s/div"
		

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
				
#				if len(self.ch1_data["header"]) == 32:
#					for i in range(0,32):
#						if not self.ch1_data["header"][i] == data[i]:
#							print "Change:",i,"value prev./now",self.ch1_data["header"][i],data[i]
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
				print "Err: Unexcepted length of data sample, no data decoded then."
				
			# compute s/div
			self.ch1_data["s_div"] = X_RANGE[data[X_SCALE_CH1]]
			self.ch1_data["s_div_index"] = data[X_SCALE_CH1]
			self.ch2_data["s_div"] = X_RANGE[data[X_SCALE_CH2]]
			self.ch2_data["s_div_index"] = data[X_SCALE_CH2]
			# check status of channels
			self.ch1_data["active"] = bool(data[CHANNEL_STATE] & 0x01)
			self.ch2_data["active"] = bool(data[CHANNEL_STATE] & 0x02)
			# x offset
			self.ch1_data["y_offset"] = 0x7e - data[Y_POS_CH1]
			#print self.ch1_x_offset
			self.ch2_data["y_offset"] = 0x7e - data[Y_POS_CH2]
			
			self.ch1_data["Bw_limit"] = bool(data[BW_LIMIT_CH1])
			self.ch2_data["Bw_limit"] = bool(data[BW_LIMIT_CH2])
			
			self.ch1_data["inverted"] = bool(data[INVERTED_CH1])
			self.ch2_data["inverted"] = bool(data[INVERTED_CH2])
			
			self.ch1_data["x_offset"] = data[X_CURSOR_CH1]
			self.ch2_data["x_offset"] = data[X_CURSOR_CH2]
			
			self.ch1_data["x_poz"] = (data[8] << 8) + data[7]
			self.ch2_data["x_poz"] = (data[40] << 8) + data[39]
			
		else:
			print "Wrn:",time.time(),"Data buffer error:",len(data)
		
	def test_screenshot(self):
		self.get_screenshot()
		for i in range(0,len(self.data)):
			try:
				if self.data_old[i] != self.data[i]:
					print "Inf: Changed to", i 
			except:
				pass
		self.data_old = self.data
		
	def get_screenshot(self, filename=""):
		self.data = ()
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)	
		#self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xcc)	
		#time.sleep(0.02)
		ts = time.time()
		self.handle.controlMsg(0x42,0xb1,None,index=0, value=0xe2)	
		time.sleep(0.05)	
		self.handle.controlMsg(0x42,0xb0,None,index=2, value=0x26)	
		#time.sleep(0.01)
		self.pixmap_data = self.handle.bulkRead(130,38912,1000)
		print "Inf: Processing time:",time.time() - ts
		print "Inf: Loaded:",len(self.pixmap_data),"bytes"
		
		pixel_data = []
		
		if len(self.pixmap_data) == 38912:
			pixel_data = self.write_pixmap(filename)
		else:
			print "Inf: Too few data for screenshot."
		return pixel_data
		
	# write binary ppm bitmap created from screenshot data from DSO
	def write_pixmap(self, filename=""):
		
		# fake file
		bitmap_data = StringIO.StringIO()
		
		# size of bitmap
		width=320; height=240
		ftype='P6' #use 'P3' for ascii, 'P6' for binary
		try:
			if filename == "":
				ppmfile=open('testimage.ppm','wb')
			else:
				ppmfile=open(filename,'wb')
					
			bitmap_data.write("%s\n" % (ftype)) 
			bitmap_data.write("%d %d\n" % (width, height)) 
			bitmap_data.write("255\n")
			
			# working with 2 bytes in one time
			for index in range(0,len(self.pixmap_data),2):
				
				# pixmapdata have exchanged even and odd bytes
				# we correct it with order of writing
				# another problem is, that one byte include TWO pixels data
				# we must shift it and then decode which color that value means
				
				color = self.pixmap_data[index+1]
				color2 = ((color) & 0x0F)
				color1 = ((color) & 0xF0) / 16
				
				color = self.pixmap_data[index]
				color4 = ((color) & 0x0F)
				color3 = ((color) & 0xF0) / 16
				
				#ppmfile.write("%c%c%c" % self.convert_to_color(color1))
				bitmap_data.write("%c%c%c" % self.convert_to_color(color1))
				
				#ppmfile.write("%c%c%c" % self.convert_to_color(color2))
				bitmap_data.write("%c%c%c" % self.convert_to_color(color2))
				
				#ppmfile.write("%c%c%c" % self.convert_to_color(color3))
				bitmap_data.write("%c%c%c" % self.convert_to_color(color3))
				
				#ppmfile.write("%c%c%c" % self.convert_to_color(color4))
				bitmap_data.write("%c%c%c" % self.convert_to_color(color4))
		
		except Exception, (s):
			print "Inf: Exception in write_pixmap:",filename," -> ",s
		
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
			return (0,0,0)
		# dark grey
		elif color == 0x01:
			return (0,0,64)
		# lighter blue
		elif color == 0x05:
			return (0,0,192)
		# red
		elif color == 0x06:
			return (0,224,0)
		#
		elif color == 0x07:
			return (128,32,0)
		# grid color - cyan
		elif color == 0x08:
			return (0,125,125)
		# dark red
		elif color == 0x09:
			return (128,32,0)
		
		elif color == 0x0A:
			return (125,125,125)
		# darker blue
		elif color == 0x0b:
			return (0,0,128)
		# cyan
		elif color == 0x0C:
			return (0,192,192)
		# yellow
		elif color == 0x0D:
			return (255,255,0)
		# red
		elif color == 0x0E:
			return (224,32,0)
		# white
		elif color == 0x0F:
			return (255,255,255)
		else:
			print "Inf: Unsuported color:", color
			return (255,255,255)	

	# test changes in data from DSO
	def test_parameters(self):
		data = dso.get_parameters()
		if self.data == None:
			self.data = data
		for i in range(0,150):
			if not self.data[i] == data[i]:
				print "Inf: Change at",i,"value prev./now",self.data[i],"/",data[i]
				
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
		print "Err: Device was not recognized or found."
