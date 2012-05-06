'''
Created on Apr 14, 2012

@author: carlos
'''

import serial
from threading import Thread
from time import sleep
from serial.serialutil import SerialException
from util import *

class SerialListener(Thread):
    '''
    classdocs
    '''

    def __init__(self, serialPort):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self._serialPort = serialPort
        self.running = False
        self.outFile = None

    def mesg_callback(self, messages, outFile=None):
        pass
        
    def parse_frame(self, frame_str):
        return frame_str

    def stop(self):
        self.running = False
        
    def write(self, message):
        self._serialPort.write(message + "\r\n")
    
    def run(self):
        self._serialPort.flushInput()
        NO_FRAME = 0
        IN_FRAME = 1
        
        new_frame = ""
        state = NO_FRAME
        self.running = True
        while self.running:
            try:
                tmp = self._serialPort.read(1)
                if tmp == '': 
                    continue
            except SerialException:
                return
            if state == NO_FRAME:
                if tmp == FSD:
                    state = IN_FRAME
                continue
            elif state == IN_FRAME:
                if tmp == FSD:
                    new_frame = ""
                    continue
                elif tmp == FED:
                    state = NO_FRAME
                    self.mesg_callback(self.parse_frame(new_frame), self.outFile)
                    new_frame = ""
                else:
                    new_frame += tmp
                    
if (__name__ == "__main__"):
    serialPort = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.001)

    sl = SerialListener(serialPort)
    sl.start()
    print "running"
    serialPort.write('H\r\n') 
    sleep(5)

    sl.stop()
    print "stop"
