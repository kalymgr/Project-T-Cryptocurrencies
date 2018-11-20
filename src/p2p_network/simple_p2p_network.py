from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout


class TLCProtocol(Protocol):
    def dataReceived(self, data):
        stdout.write(data)


class TLCClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return TLCProtocol()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print ('Connection failed. Reason:', reason)