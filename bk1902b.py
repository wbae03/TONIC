"""
Implements functions to control a BK1902B programmable power supply
Open port, set voltage, set current, output on/off, etc.
"""

# Import packages
import time
from typing import Tuple, Union
import serial


class BK1902B:
    """
    Implements functions to control a BK1902B programmable power supply
    Open port, set voltage, set current, output on/off, etc.
    """

    def __init__(self, port: str, baud: int = 9600):
        super(BK1902B, self).__init__()
        self.port = port
        self.baud = baud
        self.ser = None

    def __enter__(self):
        """
        Provides a context manager that will open but not sync, then
        delete the cache on exit.
        """
        self.open()
        return self

    def __exit__(self, excType, excValue, traceback):
        """
        Provides a context manager which will open but not sync, then
        delete the cache on exit.
        """
        self.close()

    def open(self):
        """Serial Port"""
        try:
            self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=1)
        except serial.SerialException as err:
            raise RuntimeError(f"{self.port} Unavailable") from err

    def close(self):
        """Closes serial port"""
        self.ser.close()

    @staticmethod
    def _clamp(
        val: Union[int, float], minimum: Union[int, float], maximum: Union[int, float]
    ) -> Union[int, float]:
        if minimum > maximum:
            raise ValueError("Minimum must be less than maximum")
        if val < minimum:
            return minimum
        elif val > maximum:
            return maximum
        return val

    @staticmethod
    def _toBkStr(val: Union[int, float]) -> str:
        return str(int(val * 10)).zfill(3)

    def _sendCmd(self, cmd: str):
        """Sends commands and expect "OK" as the reply"""
        if self.ser:
            self.ser.write(cmd.encode("UTF-8"))
            self.ser.flush()
            time.sleep(0.025)
            reply = self.ser.read(3)
            if reply != b"OK\r":
                raise RuntimeError(
                    f"Error encountered when sending the command: {cmd}.\n"
                    + f"Reply received: {reply}"
                )

    def set_voltage(self, voltage: float):
        """Set output voltage (between 1.0 and 60.0V)"""
        valid_voltage = self._clamp(voltage, 1, 60)
        if valid_voltage != valid_voltage:
            print(f"[!] The input voltage was clamped to {valid_voltage}")
        self._sendCmd(f"VOLT{self._toBkStr(valid_voltage)}\r")

    def set_current(self, current: float):
        """Set output voltage (between 0.0 and 15.0A)"""
        valid_current = self._clamp(current, 0, 15)
        if valid_current != valid_current:
            print(f"[!] The input voltage was clamped to {valid_current}")
        self._sendCmd(f"CURR{self._toBkStr(valid_current)}\r")

    def enable_output(self):
        """Enable output"""
        self._sendCmd("SOUT0\r")

    def disable_output(self):
        """Disable output"""
        self._sendCmd("SOUT1\r")

    def get_display(self) -> Tuple[float, float, bool]:
        """
        Reads voltage, current and CV/CC from front display
        Returns [voltage, current, is_constant_voltage]
        """
        voltage: float = 0
        current: float = 0
        is_constant_voltage: bool = False
        if self.ser:
            self.ser.flushInput()  # Flush anything left in the buffer
            self.ser.write("GETD\r".encode("UTF-8"))
            front_display_data = self.ser.read(10)
            voltage = front_display_data[0:4].rstrip()
            voltage = float(voltage) / 100
            current = front_display_data[4:8].rstrip()
            current = float(current) / 100
            is_constant_voltage = not bool(int(front_display_data[8]) - 48)
        return (voltage, current, is_constant_voltage)
