# -*- coding: utf-8 -*-
"""
File: kinesis_list.py

This file contains a routine to detect Thorlabs systems connected to the computer.

https://pylablib.readthedocs.io/en/stable/devices/Thorlabs_kinesis.html#stages-thorlabs-kinesis


.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

import time
import struct
from pylablib.devices import Thorlabs

# %% Example
if __name__ == '__main__':	
	print(Thorlabs.list_kinesis_devices())
