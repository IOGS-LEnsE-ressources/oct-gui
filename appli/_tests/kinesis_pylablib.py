# -*- coding: utf-8 -*-
"""
File: OCT_lab_app.py

This file contains test code for piezo and step motor controlling (Thorlabs).

https://pylablib.readthedocs.io/en/stable/devices/Thorlabs_kinesis.html#stages-thorlabs-kinesis


.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

import time
import struct
from pylablib.devices import Thorlabs

id_number = 0

jog_settings = {
	"mode": 2,
	"stepSize": 409600
}

def init_step_motor(id_num: str):
	# https://github.com/AlexShkarin/pyLabLib/issues/6#issue-1073743642
	step_motor = Thorlabs.BasicKinesisDevice(id_num)
	time.sleep(0.1)
	step_motor.instr.instr._flow = 256
	step_motor.instr.instr._setFlowControl()
	time.sleep(0.1)
	step_motor.instr.instr.flushInput()
	step_motor.instr.instr.flushOutput()
	time.sleep(0.1)
	step_motor.instr.instr._flow = 0
	step_motor.instr.instr._setFlowControl()

	step_motor.send_comm(messageID=0x0434)
	return step_motor
	# https://github.com/AlexShkarin/pyLabLib/issues/74

# %% Example
if __name__ == '__main__':	
	print(Thorlabs.list_kinesis_devices())

	piezo_motor = Thorlabs.KinesisPiezoController("29501399")
	step_motor = Thorlabs.KinesisMotor("40897338")
	#step_motor = Thorlabs.BasicKinesisDevice("40897338")

	# Step Motor
	print('Step Motor')
	print(step_motor.get_status())
	step_motor.setup_jog(mode=jog_settings["mode"], step_size=jog_settings["stepSize"])

	time.sleep(0.5)
	print(step_motor.get_status())

	'''
	setup_jog(mode=None, step_size=None, min_velocity=None, acceleration=None, max_velocity=None,
			  stop_mode=None, channel=None, scale=True)
	'''

	# Piezo
	print('Piezo Motor/Controller')
	print(piezo_motor.get_status())


	piezo_motor.close()