#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
#
#	QT4 application for DSO UNI-T 2XXX/3XXX
#	It allows get screenshot of screen
#
#	Ing. Tomas Kosan, 2008-2010
#
#############################################################################

import sys, time, threading, Queue, types,  csv
import os.path
from PyQt4 import QtCore, QtGui, Qt

# import converted ui file
from UI import simpleUI	

# import UNI-T class
from ut2XXX import UT2XXX, utils
# import data packet definitions
#from ut2XXX_definitions import *
# import graphic classes and utils
import graphic

version = "simpleDSO 0.3"

# from main to thread
Que_main2thread = Queue.Queue()
# thread to main
Que_thread2main = Queue.Queue()

# thread of DSO class
def DSO_thread():
	
	try:
		want_run = True
		offline = False
		
		# basic init of DSO comunication
		dso = UT2XXX.UNI_T_DSO()
		# test if device is connected
		if not dso.is_present:
			Que_thread2main.put("ERR_NOT_FOUND")
			offline = True
			want_run = False
			return

		msg = ""
		
		loop = 0
		
		while want_run:
			loop += 1
			try:
				msg = Que_main2thread.get_nowait()
			except:
				pass
			else:
				print "Dbg:Processing",msg
				# parse commands
				if msg == "END_NOW":
					want_run = False
					
				elif msg == "REMOTE_ON" and not offline:	
					dso.enter_far_mode()
					
				elif msg == "REMOTE_OFF" and not offline:	
					dso.leave_far_mode()
						
				elif msg == "GET_WAVE" and not offline:
					#print "Msg from main: get wave"
					dso.get_waveform()
					Que_thread2main.put("DATA")
					Que_thread2main.put(dso.ch1_data)	
					Que_thread2main.put(dso.ch2_data)
					Que_thread2main.put(dso.data_raw)
					#print "Data send."
				elif msg == "SAVE_SCREENSHOT" and not offline:
					Que_thread2main.put("PIXDATA")
					Que_thread2main.put(dso.get_screenshot())
						
				elif msg == "LOAD_WAVE":
					m =  Que_main2thread.get_nowait()
					#print m
					dso.parse_waveform(m)
					Que_thread2main.put("DATA")
					Que_thread2main.put(dso.ch1_data)	
					Que_thread2main.put(dso.ch2_data)
				
				elif msg == "RECONNECT":
					dso.init()
					if not dso.is_present:
						Que_thread2main.put("ERR_NOT_FOUND")
						offline = True
					else:
						offline = False
					
				# if it is integer, we have direct message	
				elif type(msg) == type(1) and not offline:
					dso.send_message(msg)
				else:
					msg = ""
#			if loop > 500:
#				loop = 0
#				dso.leave_far_mode()	
			time.sleep(0.001)	

	except Exception, (s):
		#print s
		Que_thread2main.put("EXCEPTION")
		Que_thread2main.put(s)
	print "Wrn: Thread end."
	try:
		dso.close()
	except:
		pass

# main class - GUI
class DSO_main(QtGui.QMainWindow, simpleUI.Ui_MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		
		print "Inf: DSO remote app is starting ..."
		self.setupUi(self)
		print "Inf: DSO remote app started."
				
		self.dso_thread = threading.Thread(target=DSO_thread)
		self.dso_thread.start()
				
		self.scene = graphic.DSO_Scene()
		
		self.gwScreen.setScene(self.scene)
		self.gwScreen.update()
		
		# autoupdate timer
		self.auto_timer = QtCore.QTimer()
		#self.auto_timer.start(1000)
		self.connect(self.auto_timer, QtCore.SIGNAL("timeout()"), self.updateScreen)
		
		# timer for checking msg queue
		self.timer = QtCore.QTimer()
		self.timer.start(10)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.updateState)
		
		self.updateScreen()
		
		self.loadScreenFromDso()

		self.setWindowTitle(QtGui.QApplication.translate("MainWindow", version, None, QtGui.QApplication.UnicodeUTF8))

	def reconnect(self):
		#if self.dso_thread.isAlive():
			#print "Thread allready started", self.dso_thread
		#else:
			#del self.dso_thread
			#self.dso_thread = threading.Thread(target=DSO_thread)
			#self.dso_thread.start()
		Que_main2thread.put("RECONNECT")
		
	#	
	def setTimer(self, force_stop = False):
		if not force_stop and self.auto_timer.isActive():
			self.auto_timer.stop()
		else:
			self.auto_timer.start()
			

	def updateScreen(self):
		if Que_main2thread.empty():
			Que_main2thread.put("GET_WAVE")
		
	def saveScreenshot2png(self, data):
		
		screen = QtGui.QPixmap()
		screen.loadFromData(data)
		
		screen = screen.scaledToWidth(640)
		
		self.scene.showPixmap(screen)
		
#		filename = QtGui.QFileDialog.getSaveFileName(self, u"Enter name and path to file", u"./", u"Images (*.png)", u"???")
#		if filename:
#			print screen.save(filename)
				

	def loadLWave(self):
		filename = QtGui.QFileDialog.getSaveFileName(self, u"Enter name and path to file", u"./", u"Data (*.dat)", u"???")
		if filename:
			#self.loaded_data = open(filename)
			self.setTimer(True)
			Que_main2thread.put("LOAD_WAVE")
			Que_main2thread.put(filename)

	def updateState(self):
		#print "Timer start"
		try:
			msg = Que_thread2main.get_nowait()
		except Exception:
			pass
		else:
#			print "Msg from thread:",msg
			if msg == "DATA":
				self.ch1_data = Que_thread2main.get()
				self.ch2_data = Que_thread2main.get()
				self.data_raw = Que_thread2main.get()
				self.scene.updateScreen(self.ch1_data, self.ch2_data)
			
			if msg == "ERR_NOT_FOUND":
				QtGui.QMessageBox.critical(self, u"Error", u"UNI-T DSO  not found. This error is cricital.\nTurn on DSO and connect it with PC by USB cable. Then run program again.")
				self.close()
				
			if msg == "PIXDATA":
				print "Inf: Recieve pixmap data."
				self.saveScreenshot2png(Que_thread2main.get())
				
			if msg == "EXCEPTION":
				self.setTimer(True)
				excep = Que_thread2main.get()
				print "Err: Exception in thread:",excep
				try:
					QtGui.QMessageBox.critical(self, u"Exception", u"Communication error ocured:\n"+str(excep))
				except:
					QtGui.QMessageBox.critical(self, u"Exception", u"Comunication error ocured.")

				
	
	
	def closeEvent(self, closeEvent):
		print "Inf: Closing"
		Que_main2thread.put("END_NOW")
		time.sleep(0.2)
		closeEvent.accept()

	def loadDataFromDso(self, force=True):
		if force:
			self.updateScreen()
		
	def processAction(self, action):
		if action.text() == "About":
			QtGui.QMessageBox.about(self,"Program "+version, "<b>Ing. Tomas Kosan, 2010</b> \
			<br><br>This program allows taking data from UNI-T DSOs<br>and save them to harddisk as an image or a CSV file.<br> \
			It also can take real screenshot of screen  of DSO.")
		if action.text() == "Exit":
			self.close()


	def loadScreenFromDso(self):
		Que_main2thread.put("SAVE_SCREENSHOT")
    
	def saveProgramScreen(self):
		self.image = QtGui.QPixmap(640,480)
		self.image.fill(QtCore.Qt.black)
		screenshot = QtGui.QPainter(self.image)
		self.gwScreen.render(screenshot)#, self.gwScreen.rect())
		filename = QtGui.QFileDialog.getSaveFileName(self, u"Enter name and path to file", u"./", u"Png (*.png)", u"screenshot.png")
		if filename:
			self.image.save(filename,"PNG")
    
	def setAutoUpdate(self, state):
		if state:
			self.auto_timer.start(self.updateValue.value())
		else:
			self.auto_timer.stop()

	def saveDataToCSV(self):
		self.loadDataFromDso()
		filename = QtGui.QFileDialog.getSaveFileName(self, u"Enter name and path to file", u"./", u"CSV (*.csv)", u"???")
		if filename:
			print "Inf: raw data from DSO:\n", self.data_raw
			print "Inf: Saving to", filename
			writer = csv.writer(open(filename, "wb"), delimiter=';')
			writer.writerow(self.ch1_data["samples"])
			writer.writerow(self.ch2_data["samples"])

			writer = csv.writer(open(filename.replace(".csv", "_raw.csv"), "wb"), delimiter=';')
			writer.writerow(self.data_raw)

def main(args):
	app=QtGui.QApplication(args)
	#app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app.quit)
	app.setStyle("plastique")
	mainWindow = DSO_main()
	mainWindow.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main(sys.argv)
