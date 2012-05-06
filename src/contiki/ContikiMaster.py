#!/usr/bin/python

from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from util import *
from time import sleep

number_clients = 1
channels = [25, 26]

class Contiki_Master(LineReceiver):
    def __init__(self):
        self.wait_H = True
        self.wait_ack = False
        self.has_token = True
        self.current_token = number_clients
        self.current_channel = channels[0]-1
        
    def lineReceived(self, line):
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
            print "Set channel", ord(line[1])
            self.sendLine(COMMAND_ACK) 
        elif line == COMMAND_TOKEN:
            print "Got token"
            self.has_token = True
            self.sendLine(COMMAND_ACK) 
        print line
    
    def sendMessage(self, msg):
        self.sendLine(msg)

class MasterFactory(Factory):
    def buildProtocol(self, addr):
        return Contiki_Master()

def gotProtocol(p):
    reactor.callLater(2, work, p)
    
def work(p):
    if p.has_token:
        if p.current_token < number_clients-1:
            p.current_token += 1
            p.sendLine(COMMAND_TOKEN + chr(p.current_token))
            print "ct", p.current_token
            p.has_token = False
        else:
            if p.current_channel != channels[-1]:
                p.current_channel += 1
                p.current_token = -1
                p.sendLine(COMMAND_CHAN + str(p.current_channel))
            elif p.current_channel == channels[-1]:
                p.sendLine(COMMAND_DONE)
                reactor.callLater(3, reactor.stop)
                return
    reactor.callLater(2, work, p)
                
point = TCP4ClientEndpoint(reactor, "localhost", 8010)
d = point.connect(MasterFactory())
d.addCallback(gotProtocol)
reactor.run()