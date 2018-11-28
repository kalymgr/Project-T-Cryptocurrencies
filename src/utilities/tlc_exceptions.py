"""
This file handles various custom exceptions happening on our software
"""


class TLCNetworkException(Exception):
    """
    class for network exceptions happening on tlc network
    """

    def __init__(self, msg=None):
        """

        :param msg: The message that will be stored with the exception
        """
        self.args = f'TLC Network Exception. {msg}'
