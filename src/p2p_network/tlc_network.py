import json
from time import time
from uuid import uuid4

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall

generateNodeId = lambda: str(uuid4())  # function that generates the node id


class TLCProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.state = 'HELLO'
        self.nodeId = self.factory.nodeId  # keep the node id
        self.remoteNodeId = None

        self.lcPing = LoopingCall(self.sendPing)  # Calls the sendPing method repeatedly to ping nodes
        self.lastPing = None

    def connectionMade(self):
        print("Connection from" + str(self.transport.getPeer()) + self.nodeId)

    def connectionLost(self, reason):
        # remove the node that disconnected from the peer dictionary, if it exists in the peer list
        if self.remoteNodeId in self.factory.peers:
            self.factory.peers.pop(self.remoteNodeId)
            self.lcPing.stop()
        print(self.nodeId + " disconnected")

    def dataReceived(self, data):
        # for each line of data
        for line in data.splitlines():
            line = line.strip()
            msgType = json.loads(line)['msgType']  # get the msg type

            # depending on the message received, do something
            if self.state == 'HELLO' or msgType == 'hello':  # if the node is in hello mode
                self.handleHello(line)
                self.state = 'READY'
            elif msgType == 'ping':  # if the node has received a ping message
                self.handlePing()
            elif msgType == 'pong':  # if the node has received a pong message
                self.handlePong()

    def sendHello(self):
        """
        Method for sending the hello
        :return:
        """
        hello = ('{"nodeId": "' + self.nodeId + '", "msgType": "hello"}').encode('utf8')
        self.state = 'READY'  # after I send the HELLO, I declare I'm ready to talk
        self.transport.write(hello)

    def sendPing(self):
        ping = '{"msgType": "ping"}'
        print(f'Ping sent \t\t {self.nodeId} --> {self.remoteNodeId}')
        self.transport.write(ping.encode('utf8'))

    def sendPong(self):
        pong = '{"msgType": "pong"}'
        self.transport.write(pong.encode('utf8'))

    def handlePing(self):
        self.sendPong()

    def handlePong(self):
        print(f'Pong received \t {self.nodeId} <-- {self.remoteNodeId}')
        self.lastPing = time()  # keep the timestamp

    def printPeerStatus(self):
        """
        Method that prints the peer status for a node
        :return:
        """
        # print('*** Current number of peers for node ' + self.nodeId + ' is ' + str(len(self.factory.peers)))
        print("----------------------------------------------------------")
        print("List of peers for node %s : " % self.nodeId)
        i = 0
        for peer in self.factory.peers:
            print(' - ' + peer)

    def handleHello(self, hello):
        """
        method that handles the line that is sent to the node (json string)
        :param hello: json string
        :return:
        """
        try:
            hello = json.loads(hello)  # load the json from the string
            self.remoteNodeId = hello.get('nodeId')  # get the remote node id
            if self.remoteNodeId == self.nodeId:  # case node connected to itself
                print('Connected to myself')
                self.transport.loseConnection()  # close the connection
            else:  # add the remote node id to the dictionary of peers
                self.factory.peers[self.remoteNodeId] = self
                self.lcPing.start(10)
                # print('-> Peer node ' + self.remoteNodeId + ' added to node ' + self.nodeId)
                self.printPeerStatus()
        except:
            print('Communication problem')


# in the example, Factory is used instead of ClientFactory
class TLCFactory(Factory):
    def startFactory(self):
        self.nodeId = generateNodeId()  # generate a node id
        self.peers = dict()  # initialize the dictionary containing the peers
        # print('Start factory for the node ' + self.nodeId)
        print(' I am TLCFactory with node id ' + self.nodeId)

    def buildProtocol(self, addr):
        print('Connected.')
        # return TLCProtocol(self)
        return TLCProtocol(self)
