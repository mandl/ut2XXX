#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#############################################################################
#
#	QT5 application for DSO UNI-T 2XXX/3XXX
#	It allows get screenshot of screen
#
#	Ing. Tomas Kosan, 2008-2010
#   Stefan Mandl 2021
#
#############################################################################

import sys, time, threading, types, csv, queue
import os.path
import logging
import argparse

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.Qt import PYQT_VERSION_STR
# import converted ui file
from UI import simpleUI
from ut2XXX import UT2XXX
from ut2XXX import utils

import graphic

text = 'This program is useful with UNI-T digital storage oscilloscopes UT2XXX or UT3XXX.'
version = "1.0"

# from main to threadgraphic
Que_main2thread = queue.Queue()
# thread to main
Que_thread2main = queue.Queue()


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
                logging.debug("Processing %s", msg)
                # parse commands
                if msg == "END_NOW":
                    want_run = False

                elif msg == "REMOTE_ON" and not offline:
                    dso.enter_far_mode()

                elif msg == "REMOTE_OFF" and not offline:
                    dso.leave_far_mode()

                elif msg == "GET_WAVE" and not offline:
                    dso.get_waveform()
                    Que_thread2main.put("DATA")
                    Que_thread2main.put(dso.ch1_data)
                    Que_thread2main.put(dso.ch2_data)
                    Que_thread2main.put(dso.data_raw)

                elif msg == "SAVE_SCREENSHOT" and not offline:
                    Que_thread2main.put("PIXDATA")
                    Que_thread2main.put(dso.get_screenshot())

                elif msg == "LOAD_WAVE":
                    m = Que_main2thread.get_nowait()
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

    except Exception as ex:
        logging.info(ex)
        Que_thread2main.put("EXCEPTION")
    # Que_thread2main.put(s)
    logging.error("Thread end.")
    try:
        dso.close()
    except:
        pass


# main class - GUIDSO_Scene
class DSO_main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = simpleUI.Ui_MainWindow()
        logging.info("DSO remote app is starting (Qt: % s pyQt: %s)",QT_VERSION_STR, PYQT_VERSION_STR)
        self.ui.setupUi(self)
        logging.info("DSO remote app started.")

        self.dso_thread = threading.Thread(target=DSO_thread)
        self.dso_thread.start()

        self.scene = graphic.DSO_Scene()

        self.ui.gwScreen.setScene(self.scene)
        self.ui.gwScreen.update()

        # autoupdate timer
        self.auto_timer = QtCore.QTimer()
        self.auto_timer.timeout.connect(self.updateScreen)

        # timer for checking msg queue
        self.timer = QtCore.QTimer()
        self.timer.start(10)
        self.timer.timeout.connect(self.updateState)

        #self.updateScreen()
        #self.loadScreenFromDso()

        self.setWindowTitle(QApplication.translate("MainWindow", "SimpleDSO " + version, None, -1))

    def reconnect(self):
        # if self.dso_thread.isAlive():
        # print "Thread allready started", self.dso_thread
        # else:
        # del self.dso_thread
        # self.dso_thread = threading.Thread(target=DSO_thread)
        # self.dso_thread.start()
        Que_main2thread.put("RECONNECT")

    #
    def setTimer(self, force_stop=False):
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


    def loadLWave(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, u"Enter name and path to file", u"./", u"Data (*.dat)",
                                                     u"???")
        if filename:
            # self.loaded_data = open(filename)
            self.setTimer(True)
            Que_main2thread.put("LOAD_WAVE")
            Que_main2thread.put(filename)

    def updateState(self):
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
                QMessageBox.critical(self, self.tr("Error"),
                                     self.tr("UNI-T DSO  not found. This error is cricital.\n \
                                    Turn on DSO and connect it with PC by USB cable. Then run program again."))
                self.close()

            if msg == "PIXDATA":
                logging.info("Recieve pixmap data.")
                self.saveScreenshot2png(Que_thread2main.get())

            if msg == "EXCEPTION":
                self.setTimer(True)
                excep = Que_thread2main.get()
                logging.error("Exception in thread: %s", excep)
                try:
                    QtGui.QMessageBox.critical(self, u"Exception", u"Communication error ocured:\n" + str(excep))
                except:
                    QtGui.QMessageBox.critical(self, u"Exception", u"Comunication error ocured.")

    def closeEvent(self, closeEvent):
        logging.info("Closing")
        Que_main2thread.put("END_NOW")
        time.sleep(0.2)
        closeEvent.accept()

    def loadDataFromDso(self):
        self.updateScreen()

    def processAction(self, action):
        if action.text() == "About":
            QMessageBox.about(self, "Program " + version, "<b>Ing. Tomas Kosan, 2010</b> \
			<br><br>This program allows taking data from UNI-T DSOs<br>and save them to harddisk as an image or a CSV file.<br> \
			It also can take real screenshot of screen  of DSO.")
        if action.text() == "Exit":
            self.close()

    def loadScreenFromDso(self):
        Que_main2thread.put("SAVE_SCREENSHOT")

    def saveProgramScreen(self):
        self.image = QtGui.QPixmap(640, 480)
        self.image.fill(QtCore.Qt.black)
        screenshot = QtGui.QPainter(self.image)
        self.ui.gwScreen.render(screenshot)  # , self.gwScreen.rect())
        filename = QFileDialog.getSaveFileName(self, self.tr("Enter name and path to file"), u"./", self.tr("Png (*.png)"),
                                               self.tr("screenshot.png"))
        if filename:
            self.image.save(filename[0], "PNG")

    def setAutoUpdate(self, state):
        if state:
            self.auto_timer.start(self.ui.updateValue.value())
        else:
            self.auto_timer.stop()

    def saveDataToCSV(self):
        self.loadDataFromDso()
        filename = QFileDialog.getSaveFileName(self, self.tr("Enter name and path to file"), u"./", self.tr("CSV (*.csv)"), u"???")
        if filename:
            logging.debug("raw data from DSO: %s\n", self.data_raw)
            logging.debug("Saving to %s", filename)
            writer = csv.writer(open(filename[0] + ".csv", "w", newline=''), delimiter=';')
            writer.writerow(self.ch1_data["samples"])
            writer.writerow(self.ch2_data["samples"])

            writer = csv.writer(open(filename[0] + "_raw.csv", "w", newline=''), delimiter=';')
            writer.writerow(self.data_raw)

# set log level
def setup_logging(verbosity):
    base_loglevel = 30
    verbosity = min(verbosity, 2)
    loglevel = base_loglevel - (verbosity * 10)
    logging.basicConfig(level=loglevel,
                        format='%(levelname)s: %(message)s')

def main(args2):
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument('-v', '--verbose',
                    action='count',
                    dest='verbosity',
                    default=0,
                    help="verbose output (repeat for increased verbosity)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="Version {} using Qt: {} pyQt: {}".format(version,QT_VERSION_STR, PYQT_VERSION_STR))

    # Read arguments from the command line
    args = parser.parse_args()

    #setup logging
    setup_logging(args.verbosity)
 
   
    app = QApplication(args2)
    app.setStyle("plastique")
    mainWindow = DSO_main()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
