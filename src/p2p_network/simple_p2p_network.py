import json
from uuid import uuid4

from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout


class TLCProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.nodeId = factory.nodeId  # keep the node id

        self.state = 'HELLO'
        self.remoteNodeId = None

    def dataReceived(self, data):
        # stdout.write(data)
        # print('receiving some data' + str(data))
        # self.transport.write(data)

        # for each line of data
        for line in data.splitlines():
            line = line.strip()
            if self.state == 'HELLO':  # if the node is in hello mode
                self.handleHello(line)
                self.state = 'READY'

    def handleHello(self, hello):
        """
        method that handles the line that is sent to the node (json string)
        :param hello: json string
        :return:
        """
        print('handleHello called')
        # replace the double quotes with single quotes

        try:
            hello = json.loads(hello)  # load the json from the string
            self.remoteNodeId == hello.get('nodeId')  # get the remote node id
            if self.remoteNodeId == self.nodeId:  # case node connected to itself
                print('Connected to myself')
                self.transport.loseConnection()  # close the connection
            else:  # add the remote node id to the dictionary of peers
                self.factory.peers[self.remoteNodeId] = self
        except:
            print('Communication problem')

    def sendHello(self):
        """
        Method for sending the hello
        :return:
        """
        hello = ('{"nodeId": " ' + self.nodeId + '", "msgType": "hello"}').encode('utf8')
        # self.transport.write((hello + '\n').encode('utf8'))
        self.transport.write(hello)

    def connectionMade(self):
        print("Connection made by " + str(self.transport.getPeer()))

    def connectionLost(self, reason):
        print('Connection Lost from node ')
        if self.remoteNodeId is not None:  # print the name of the node, if it exists
            print(self.remoteNodeId)
        # remove the node that disconnected from the peer dictionary
        if self.remoteNodeId in self.factory.peers:
            self.factory.peers.pop(self.remoteNodeId)


# in the example, Factory is used instead of ClientFactory.
class TLCClientFactory(ClientFactory):

    def startFactory(self):
        self.peers = dict()  # initialize the dictionary containing the peers
        self.nodeId = str(uuid4())  # generate a node id
        print('Start factory for the node ' + self.nodeId)

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return TLCProtocol(self)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print ('Connection failed. Reason:', reason)