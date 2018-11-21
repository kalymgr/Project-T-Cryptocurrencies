import json
from uuid import uuid4

from twisted.internet.protocol import Protocol, Factory


generateNodeId = lambda: str(uuid4())


class TLCProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.state = 'HELLO'
        self.nodeId = self.factory.nodeId  # keep the node id
        self.remoteNodeId = None

    def connectionMade(self):
        print("Connection from" + str(self.transport.getPeer()) + self.nodeId)

    def connectionLost(self, reason):
        # remove the node that disconnected from the peer dictionary
        if self.remoteNodeId in self.factory.peers:
            self.factory.peers.pop(self.remoteNodeId)
        print(self.nodeId + " disconnected")

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

    def sendHello(self):
        """
        Method for sending the hello
        :return:
        """
        hello = ('{"nodeId": "' + self.nodeId + '", "msgType": "hello"}').encode('utf8')
        self.transport.write(hello)

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

            # print('I am ' + self.nodeId + ' and my peers are ' + str(self.factory.peers))
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
