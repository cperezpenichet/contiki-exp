#!/usr/bin/python

from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from util import *
from SerialListener import SerialListener
import serial

out_Path = "./"

path_prefix = '/dev/ttyUSB'
motes = [0, 1]

class Contiki_Client(LineReceiver):
    def __init__(self):
        self.wait_H = True
        self.wait_ack = False
        self.mote_serials = []
        print motes
        for mote in motes:
            serialPort = serial.Serial(path_prefix + str(mote), 115200, timeout=0.05)
            sl = SerialListener(serialPort)
            sl.mesg_callback = self.serial_callback
            sl.outFile = file( out_Path + "Node_" + str(mote) + ".txt", 'a' )
            sl.start()
            self.mote_serials.append(sl)
        self.current_node = 0
        self.has_token = False
        
    def serial_callback(self, message, file = None):
        print "SERIAL:", message
        if (message[0] == COMMAND_DONE) and self.has_token:
            if self.current_node == len(self.mote_serials)-1:
                self.sendLine(COMMAND_TOKEN)
                self.has_token = False
                self.current_node = 0
            else:
                self.current_node += 1
                self.mote_serials[self.current_node].write(COMMAND_TOKEN)
        elif message[0] == COMMAND_ACK:
            return
        else:
            file.write(message+'\n')
        
    def lineReceived(self, line):
        print "TCP:", line
        if self.wait_ack:
            if line == COMMAND_ACK:
                self.wait_ack = False
            else:
                return
        if self.wait_H:
            if line == COMMAND_HELO:
                self.wait_H = False
                self.wait_ack = True
                self.sendLine(COMMAND_HELO)
            else:
                return
        if line[0] == COMMAND_CHAN:
            print "Set channel", line[1:]
            self.sendLine(COMMAND_ACK)
            for mote in self.mote_serials:
                mote.write(COMMAND_CHAN + line[1:]) 
        elif line == COMMAND_TOKEN:
            self.has_token = True
            print "Got token"
            self.mote_serials[self.current_node].write(COMMAND_TOKEN)
            self.sendLine(COMMAND_ACK)
        elif line[0] == COMMAND_DONE:
            self.finish()
            
    def finish(self):
        for mote in self.mote_serials:
            mote.outFile.close()
            mote.stop()
        reactor.stop()
    
    def sendMessage(self, msg):
        self.sendLine(msg)

class ClientFactory(Factory):
    def buildProtocol(self, addr):
        return Contiki_Client()

def gotProtocol(p):
#    reactor.callLater(2, p.transport.loseConnection)
    pass

point = TCP4ClientEndpoint(reactor, "localhost", 8010)
d = point.connect(ClientFactory())
d.addCallback(gotProtocol)
reactor.run()