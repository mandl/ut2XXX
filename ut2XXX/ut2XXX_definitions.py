#!/usr/bin//python
# -*- coding: utf-8 -*-

####################################################################
#   Definice komunikacnich prikazu pro osciloskop UT2062C          #
#   Definitions of commands for communication with DSO             #
#                                                                  #
#   Ing. Košan Tomáš, prosinec 2008                                #
#                                                                  #
#   Licence: GNU GPL v2                                            #
####################################################################


X_OFFSET_NULL = 3803

# prikazy pro vzdalene ovladani
# remote control commands

# switch on/off remote control
# zapne/vypne vzdalene ovladani
REMOTE_ON  = 0xf0
REMOTE_OFF = 0xf1

# F1 - F5 buttons
# tlacitka F1 - F5
BTN_F1 = 0xf7
BTN_F2 = 0xf6
BTN_F3 = 0x03
BTN_F4 = 0x04
BTN_F5 = 0x05

# display control buttons
# tlacitka pro zobrazovani
BTN_CH1  = 0x07
BTN_CH2  = 0x09
BTN_MATH = 0x0a
BTN_REF  = 0x0b
BTN_OFF  = 0x18

# funtion buttons
# tlacitka funkci
BTN_MEAS     = 0x16
BTN_ACQU     = 0x1c
BTN_STOR     = 0x22
BTN_RUN_STOP = 0x28
BTN_CURSOR   = 0x17
BTN_DISPLAY  = 0x1d
BTN_UTILITY  = 0x23
BTN_AUTO     = 0x29
BTN_MENU     = 0x24

# X axis control
# ovladani X osy
VOLTS_UP = 0x36
VOLTS_DN = 0x35
VERT_UP  = 0x33
VERT_DN  = 0x34
SET_TO_0 = 0x0c

# Y axis control
# ovladani Y osy
SEC_DIV_UP = 0x39
SEC_DIV_DN = 0x3a
HORIZ_UP   = 0x38
HORIZ_DN   = 0x37

# trigger control
# ovladani trigeru
TRIG_UP    = 0x3b
TRIG_DN    = 0x3c
MENU_TRIG  = 0x2e
SET_TO_50  = 0x2f
FORCE_TRIG = 0x30

# univerzal turnning part
# univerzalni tocitko
UNI_PLUS  = 0x31
UNI_MINUS = 0x32

# help
# napoveda
BTN_HELP = 0x2a

# data load
# nacitani dat
DATA_CH1 = 0xf9
DATA_CH2 = 0xfa
GET_WAVE = 0x06


# Y axis range in V/div
Y_RANGE = [2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3, 1, 2, 5]

# x axis range in s/div
X_RANGE = [0, 20E-10, 5E-9, 10E-9, 20E-9, 50E-9, 100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, \
           10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6,
	       1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3, 1, 2, 5, 10, 20, 50]
	
# channel coupling 
COUPLING = ["DC","AC","GND"]

 # offset between channel data 1 and 2
CH_OFFSET    = 32
	
# indexes of data sections
#  0 – CH1            active
#  1 – CH2            active
#  2 – CH2 and CH1    active
CHANNEL_STATE = 2

# some data ???
#   2 - math active
CHANNEL_INFO_INDEX = 4

# y sense index V/div
Y_SENSE_CH1  = 5
Y_SENSE_CH2  = Y_SENSE_CH1 + CH_OFFSET	

# y position wave
Y_POS_CH1    = 6
Y_POS_CH2    = Y_POS_CH1 + CH_OFFSET

# x position wave
X_POS_LSB_CH1 = 7
X_POS_MSB_CH1 = 8
X_POS_LSB_CH2 = 7 + CH_OFFSET
X_POS_MSB_CH2 = 8 + CH_OFFSET

# channel inverted
INVERTED_CH1= 9
INVERTED_CH2= 9 + CH_OFFSET

# x scale index s/div
X_SCALE_CH1 = 10
X_SCALE_CH2 = 10 + CH_OFFSET

# X curser position
X_CURSOR_CH1 = 11
X_CURSOR_CH2 = 11 + CH_OFFSET

# channel coupling index
COUPLING_CH1 = 12
COUPLING_CH2 = COUPLING_CH1 + CH_OFFSET

# Bandwide limit active
BW_LIMIT_CH1= 15
BW_LIMIT_CH2= 15 + CH_OFFSET

# Probe x1 x10 x100 x1000
Y_PROBE_CH1  = 19
Y_PROBE_CH2  = Y_PROBE_CH1 + CH_OFFSET

# Index 20 ?

# Index 21 ?
