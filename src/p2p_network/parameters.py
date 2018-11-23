"""
File that stores some parameters related to the specific node running
"""


class NodeTypes:
    """
    class holding the types of nodes
    """
    FULL_NODE = 1
    NOT_FULL_NODE = 0


class Parameters:
    """
    class holding some general parameters
    """
    PROTOCOL_VERSION = 1  # the higher protocol version that this node can understand
    NODE_TYPE = NodeTypes.FULL_NODE  # the type of the node - let's suppose this is a full node
    NODE_IP_ADDRESS = 'localhost'  # the ip address of the node
    NODE_DEFAULT_PORT = 8010  # the default port of the node
