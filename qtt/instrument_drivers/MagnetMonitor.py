import os
import sys
import glob
import getopt

from datetime import datetime
from qcodes.instrument_drivers.american_magnets.AMI430_IP import AMI430
from qtt.instrument_drivers.DistributedInstrument import InstrumentDataClient
from qtt.instrument_drivers.DistributedInstrument import InstrumentDataServer

# -----------------------------------------------------------------------------


class MagnetDataReceiver(InstrumentDataClient):
    ''' Receives and sends magnet data from the AMI430 server connection.'''

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.add_get_command('_setpoint', 'T', -1, 'Gets the field.')
        self.add_get_command('_in_persistent_mode', 'T', -1, 'Persistent mode status.')

"""
client = MagnetDataReceiver(name='AMI magnet', port=10501)
print(client._setpoint())
print(client._in_persistent_mode())
# client.setpoint({'value': 4})
"""

# -----------------------------------------------------------------------------


class MagnetDataSender(InstrumentDataServer):

    def __init__(self, **kwargs):
        magnet = AMI430.AMI430(name='magnet', address='192.168.0.11', write_confirmation=False,
                               port=7180, coil_constant=0.422, current_rating=0.237,
                               current_ramp_limit=0.02, server_name=None)
        quantities = {'_setpoint': magnet.setpoint.get,
                      '_in_persistent_mode': magnet.in_persistent_mode}
        _data_server_ = InstrumentDataServer(quantities, **kwargs)
        _data_server_.run()

"""
server = MagnetDataSenders(port=10501)
"""

# -----------------------------------------------------------------------------
