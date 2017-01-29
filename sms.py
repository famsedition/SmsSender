#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# Sending a SMS with Python and pyserial via an USB 3G Modem
# tested with: Huawei Technologies Co., Ltd. E3533 USB Modem
# and a orange SIM card

import serial
from curses import ascii
import time
import sys
import getopt

baudrate = 9600
device = "/dev/ModemOrange"
simpin = 0000


def getline(ser):
    buf = ""
    while True:
        ch = ser.read(1)
        if ch == '\r':
            break
        buf += ch
    return buf


def send_sms(message, phonenumber):
    # Initialize serial connection to 3G USB Modem
    result = "Error"
    modem = serial.Serial(device, baudrate, timeout=5)
    print "Connected to " + modem.name
    # Check modem status
    modem.write(b'AT\r')
    sent_cmd = getline(modem)
    response = modem.read(4)
    if "OK" in response:
        print "Modem Status: OK"
        # check pin and enter it if needed
        modem.write(b'AT+CPIN?\r')
        sent_cmd = getline(modem)
        line2 = getline(modem)  # empty
        line3 = getline(modem)  # empty
        response = getline(modem)  # get OK
        if "SIM PIN" in response:
            print "Sending PIN to modem ... "
            modem.write(b'AT+CPIN="%s"' % simpin)
            sent_cmd = getline(modem)
            response = getline(modem)
            print response
        elif "READY" in response:
            print "PIN already entered."
        # set modem to text mode
        modem.write(b'AT+CMGF=1\r')
        sent_cmd = getline(modem)
        response = getline(modem)
        if "OK" in response:
            print "Modem set to text mode!"
            # send sms
            print "Sending sms ..."
            modem.write(b'AT+CMGS="%s"\r' % phonenumber)
            time.sleep(0.5)
            modem.write(b'%s\r' % message)
            time.sleep(0.5)
            modem.write(ascii.ctrl('z'))
            time.sleep(0.5)
            response = modem.readlines()
            if "+CMGS" in response[-3]:
                result = "Success"
                print "Success! SMS sent to %s"%phonenumber
            else:
                print "Error: SMS not sent!"
        else:
            print "Error: Setting modem to text mode failed!"
    elif "NO CARRIER" in response:
        print "Error: No 3G connection!"
    else:
        print "Error: Something else failed!"
    modem.close()
    return result
