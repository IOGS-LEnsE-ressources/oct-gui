import os
import time
import sys
import clr
#from win32cryptcon import SCHANNEL_ENC_KEY

if os.path.exists("C:\\Program Files\\Thorlabs\\Kinesis\\"):
    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.StepperMotorCLI.dll")
    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.PiezoCLI.dll")
    from Thorlabs.MotionControl.DeviceManagerCLI import *
    from Thorlabs.MotionControl.GenericMotorCLI import *
    from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import *
    from Thorlabs.MotionControl.KCube.PiezoCLI import *
    from System import Decimal  # necessary for real world units

    class Motor:
        """
        Class for controlling Thorlabs BSC20x step motor, through a DRV208 controller.
        """
        def __init__(self, parent, serial_no = "40897338"):
            self.serial_no = serial_no
            try:
                # device_list = DeviceManagerCLI.BuildDeviceList()

                # Connect, begin polling, and enable
                self.device = BenchtopStepperMotor.CreateBenchtopStepperMotor(self.serial_no)
                self.device.Connect(self.serial_no)
                self.parent = parent
                time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

                # For benchtop devices, get the channel
                self.channel = self.device.GetChannel(1)

                # Ensure that the device settings have been initialized
                if not self.channel.IsSettingsInitialized():
                    self.channel.WaitForSettingsInitialized(10000)  # 10 second timeout
                    assert self.channel.IsSettingsInitialized() is True

                # Start polling and enable
                self.channel.StartPolling(250)  # 250ms polling rate
                time.sleep(0.25)
                self.channel.EnableDevice()
                time.sleep(0.25)  # Wait for device to enable

                # Get Device Information and display description
                device_info = self.channel.GetDeviceInfo()
                #print(device_info.Description)
                #print(f'Device ID : {channel.DeviceID}')

                ## Load any configuration settings needed by the controller/stage
                channel_config = self.channel.LoadMotorConfiguration(self.channel.DeviceID)
                chan_settings = self.channel.MotorDeviceSettings

                self.channel.GetSettings(chan_settings)
                channel_config.DeviceSettingsName = 'DRV208'
                channel_config.UpdateCurrentConfiguration()
                self.channel.SetSettings(chan_settings, True, False)

                #print(f'Position = {channel.DevicePosition}')

                ## Get parameters related to homing/zeroing/other
                # Home or Zero the device (if a motor/piezo)
                if __name__ == "__main__":print("Retour à zéro du moteur")
                self.channel.Home(50000)
                if __name__ == "__main__":print("Retour à zéro effectué")

                self.pos = self.get_position()

            except Exception as e:
                # this can be bad practice: It sometimes obscures the error source
                print(e)

        def move_motor(self, position:float, offset:float = 0, sleep_time = 0.1):
            """
            Move the motor to the position.
            :param position: desired position, in mm.
            :param sleep_time: Pause between movement of the motor, in s.
            """
            if float(self.parent.motor_max_pos) >= position >= 0:
                if __name__ == "__main__":print("Mise en position du moteur ...")
                self.channel.MoveTo(Decimal(position - offset), 50000)  # Move to 1 mm
                self.pos = self.get_position()
                if __name__ == "__main__":print(f"Position = {self.pos}mm")

            else:
                print(f"la position choisie doit être comprise entre 0 et {round(float(self.parent.motor_max_pos), 3)}mm")

        def set_motor_displacement(self, direction : bool, delta_z : float):
            """
            direction = 1 : up
            direction = 0 : down
            """
            self.pos = self.get_position()
            print("déplacement du moteur")
            if direction:
                self.move_motor(self.pos + delta_z)
            else:
                self.move_motor(self.pos - delta_z)

        def home_motor(self, sleep_time = 0.1):
            """
            Move the motor to its home position.
            :param sleep_time: Pause between movement of the motor, in s.
            """
            #time.sleep(sleep_time)  # Useful ?
            if __name__ == "__main__":print("Retour à zéro du moteur")
            self.channel.Home(50000)
            if __name__ == "__main__":print("Retour à zéro effectué")
            #time.sleep(sleep_time)

        def disconnect_motor(self):
            """
            Disconnect the motor.
            """
            self.channel.StopPolling()
            self.device.Disconnect()

        def get_position(self):
            position = str(self.channel.DevicePosition).replace(',','.')
            return float(position)

        def find_motor(self):
            self.device.Connect(self.serial_no)
            time.sleep(0.25)


    class Piezo:
        """
        Class for controlling Thorlabs KPZ step motor, through a DRV208 controller.
        """
        def __init__(self, serial_no = "29501399"):
            #SimulationManager.Instance.InitializeSimulations()
            self.serial_no = serial_no  # Replace this line with your device's serial number
            print(f"Initialisation...")
            DeviceManagerCLI.BuildDeviceList()

            # Connect, begin polling, and enable
            self.device = KCubePiezo.CreateKCubePiezo(self.serial_no)

            self.device.Connect(self.serial_no)

            # Get Device Information and display description
            device_info = self.device.GetDeviceInfo()
            #print(device_info.Description)

            # Start polling and enable
            self.device.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            self.device.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.device.IsSettingsInitialized() is True

            # Load the device configuration
            device_config = self.device.GetPiezoConfiguration(self.serial_no)

            # This shows how to obtain the device settings
            device_settings = self.device.PiezoDeviceSettings

            # Set the Zero point of the device
            #print("Setting Zero Point")
            self.device.SetZero()

            # Get the maximum voltage output of the KPZ
            max_voltage = self.device.GetMaxOutputVoltage()  # This is stored as a .NET decimal
            #print(f'Max voltage {max_voltage}')
            self.device.SetMaxOutputVoltage(max_voltage)

            self.max_voltage = max_voltage
            print(f"Piezo initialisé")

        def set_voltage_piezo(self, voltage: float, SleepTime = 0.3):
            """
            Set a voltage to the piezo controller.
            :param voltage: voltage, in V.
            """
            max_voltage = self.max_voltage
            dev_voltage = Decimal(voltage)

            if dev_voltage != Decimal(0) and dev_voltage <= max_voltage:
                self.device.SetOutputVoltage(dev_voltage)
                #time.sleep(SleepTime)
                if __name__ == "__main__":print(f"Tension appliquée {self.device.GetOutputVoltage()}")
            elif dev_voltage == Decimal(0):
                self.device.SetZero()
                if __name__ == "__main__":print(f"Tension appliquée {self.device.GetOutputVoltage()}")
            else:
                if __name__ == "__main__":print(f'La tension doit être inférieure à {max_voltage}')

        def set_zero_piezo(self):
            self.device.SetZero()
            if __name__ == "__main__":print(f"Piezo placé en zéro")

        def disconnect_piezo(self):
            self.device.StopPolling()
            self.device.Disconnect()

        def get_voltage(self):
            return self.device.GetOutputVoltage()

        def find_piezo(self):
            self.device.Connect(self.serial_no)

else:
    class Motor:
        """
        Class for controlling Thorlabs BSC20x step motor, through a DRV208 controller.
        """

        def __init__(self, serial_no="40897338"):
            self.serial_no = serial_no
            self.position = 3

        def move_motor(self, position: float, sleep_time=0.1):
            self.position = position

        def set_motor_displacement(self, direction: bool, delta_z: float):
            if direction == 1:
                self.position += delta_z
            else:
                self.position -= delta_z

        def home_motor(self, sleep_time=0.1):
            pass

        def disconnect_motor(self):
            """
            Disconnect the motor.
            """
            pass

        def get_position(self):
            return self.position


    class Piezo:
        """
        Class for controlling Thorlabs KPZ step motor, through a DRV208 controller.
        """

        def __init__(self, serial_no="29501399"):
            # SimulationManager.Instance.InitializeSimulations()
            self.serial_no = serial_no  # Replace this line with your device's serial number
            pass

        def set_voltage_piezo(self, voltage: float, SleepTime=0.3):
            pass

        def set_zero_piezo(self):
            pass

        def disconnect_piezo(self):
            pass

        def get_voltage(self):
            return 5.2


if __name__ == "__main__":
    P = Piezo()
    M = Motor()
    time.sleep(1)
    P.set_voltage_piezo(2)
    time.sleep(1)
    P.set_voltage_piezo(4)
    time.sleep(1)
    P.set_voltage_piezo(8)
    time.sleep(1)
    P.set_voltage_piezo(10)
    time.sleep(1)
    P.set_voltage_piezo(12)
    time.sleep(1)
    P.set_voltage_piezo(14)
    P.disconnect_piezo()
    M.disconnect_motor()