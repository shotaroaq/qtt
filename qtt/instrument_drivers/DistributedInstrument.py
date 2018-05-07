import logging
from functools import partial

from zmqrpc.ZmqRpcClient import ZmqRpcClient
from zmqrpc.ZmqRpcServer import ZmqRpcServerThread

from qcodes import Instrument

# -----------------------------------------------------------------------------


class InstrumentDataClient(Instrument):
    """
    A proxy client for collecting instrument measurable quantities
    from a server.

    Args:
        name (str): the name of the instrument.
        address (str): the ip-address of the server.
        port (int): the port number of the proxy server.
        user (str): a username for protection.
        password (str): a password for protection.
    """

    def __init__(self, name, address='localhost', port=8080, user=None,
                 password=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__client = ZmqRpcClient(["tcp://{0}:{1}".format(address, port)],
                                     username=user, password=password)
        self.sec_timeout = 3

    def __proxy_wrapper(self, function_name, function_parameters, default_value):
        try:
            return self.__client.invoke(function_name, function_parameters,
                                        time_out_waiting_for_response_in_sec=self.sec_timeout)
        except Exception as ex:
            logging.warning(ex)
            return default_value

    def add_get_command(self, quantity, get_cmd_name, unit, default_value, doc_string, parameters=None):
        """Adds a instument function to the dataclient."""
        if not quantity:
            quantity = get_cmd_name
        command = partial(self.__proxy_wrapper, get_cmd_name, parameters, default_value)
        self.add_parameter(quantity, unit=unit, get_cmd=command, docstring=doc_string)

    def add_set_command(self, quantity, set_cmd_name, unit, default_value, doc_string):
        """Adds a instument function to the dataclient."""
        if not quantity:
            quantity = set_cmd_name
        command = partial(self.__proxy_wrapper, set_cmd_name, default_value=default_value)
        self.add_parameter(quantity, unit=unit, set_cmd=command, docstring=doc_string)

# -----------------------------------------------------------------------------


class InstrumentDataServer():
    """
    Represents a server proxy for sending instrument measurable quantities
    to a client.

    Args:
        functions (dict): the instrument functions.
        address (str): the ip-address of the server.
        port (int): the port number of the proxy server.
        user (str): a username for protection.
        password (str): a password for protection.
    """

    def __init__(self, functions, address='*', port=8080, user=None, password=None):
        self._server_ = ZmqRpcServerThread("tcp://{0}:{1}".format(address, port),
                                           rpc_functions=functions, username=user,
                                           password=password)

    def run(self):
        """Starts the server proxy and blocks the current thread. A keyboard
        interuption will stop and clean-up the server proxy."""
        print(' Enabled instrument server...')
        print(' Press CTRL+C to quit!')
        try:
            self._server_.start()
            while True:
                continue
        except KeyboardInterrupt:
            print(' Done')
        finally:
            self._server_.stop()
            self._server_.join()

    def start(self):
        """Starts the server proxy."""
        self._server_.start()

    def stop(self):
        """Stops the server proxy."""
        self._server_.stop()

# -----------------------------------------------------------------------------
