"""
File that stores some parameters related to the specific node running
"""


class NodeTypes:
    """
    Class holding the types of nodes. Depending on the type, a node can provide a set of services.
    """
    NOT_FULL_NODE = 0  # other types of nodes that can provide less services than full nodes
    FULL_NODE = 1  # a simple full node
    SEED_NODE = 2  # a node used as a seed, for discovering peers


class Parameters:
    """
    class holding some general parameters
    """
    PROTOCOL_VERSION = 1  # the higher protocol version that this node can understand
    NODE_TYPE = NodeTypes.FULL_NODE  # the type of the node - let's suppose this is a full node
    NODE_IP_ADDRESS = 'localhost'  # the ip address of the node
    NODE_DEFAULT_PORT_MAINNET = 8010  # the default port of the node - mainnet
    NODE_DEFAULT_PORT_TESTNET = 8020  # the default port of a node for testnet

    TIME_OF_CON_INACTIVITY_INTERVAL = 5 * 60  # the interval for increasing the time of connection inactivity
    CHECK_CON_INACTIVITY_INTERVAL = 5 * 60  # the interval for checking the time of connection inactivity
    CLOSE_CONNECTION_TIME_LIMIT = 90 * 60  # the time of inactivity after which the connection should be closed
    CON_INACTIVITY_PING_LIMIT = 30 * 60  # the time limit after which the node should send a ping to his peer

    BLOCK_VERSION = 1  # the block version. Used to choose validation rules
    TARGET_THRESHOLD = 1  # the target threshold for the proof of work mining algorithm (mining difficulty)
    MAX_NUMBER_OF_BLOCKS_SENT = 16  # the maximum number that can be sent in one group. Bitcoin uses 128.
    # Problem is that, due to the tcp methods I use, 128 is too large (not all bytes are sent). So I use 16
