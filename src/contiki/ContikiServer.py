#!/usr/bin/python

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from util import *
from threading import Thread

class Client_Connection(LineReceiver):
    def __init__(self, clients):
        self.clients = clients
        self.wait_H   = True
        self.wait_ack = False
    
    def connectionMade(self):
        self.sendLine(COMMAND_HELO)
        self.wait_H = True
        self.wait_ack = False
    
    def connectionLost(self, reason):
        if self in self.clients:
            self.clients.remove(self)
    
    def lineReceived(self, line):
        if self.wait_ack:
            if line == COMMAND_ACK:
                self.wait_ack = False
            else:
                return
        if self.wait_H:
            if line == COMMAND_HELO:
                self.sendLine(COMMAND_ACK)
                self.clients.append(self)
                self.wait_H = False
            else:
                return
        if line[0] == COMMAND_CHAN or line[0] == COMMAND_DONE:
            for client in self.clients:
                if client != self:
                    client.sendLine(line)
        if line[0] == COMMAND_TOKEN:
            if len(line) > 1:
                self.clients[ord(line[1])].sendLine(COMMAND_TOKEN)
            else:
                self.clients[-1].sendLine(COMMAND_TOKEN)
        print line
    
class Connection_Factory(Factory):
    def __init__(self):
        self.clients = []
    
    def buildProtocol(self, addr):
        return Client_Connection(self.clients)
    
reactor.listenTCP(8010, Connection_Factory())
print "listening on port 8010"
reactor.run()