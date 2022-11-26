from lewis.adapters.stream import StreamInterface, Cmd
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder

class Mode(object):
    MODES = []

class OutputMode(Mode):
    ON = "1"
    OFF = "0"
    MODES = [ON, OFF]
    
@has_log
class Keithley2290StreamInterface(StreamInterface):

    # Commands that we expect via serial during normal operation
    commands = {
        # Readback values
        CmdBuilder("get_idn").escape("*IDN?").eos().build(),
        CmdBuilder("get_volt").escape("VOUT?").eos().build(),
        CmdBuilder("get_volt_limit").escape("VLIM?").eos().build(),
        CmdBuilder("get_curr").escape("IOUT?").eos().build(),
        CmdBuilder("get_curr_trip").escape("ITRP?").eos().build(),
        CmdBuilder("get_curr_limit").escape("ILIM?").eos().build(),
        CmdBuilder("get_setting_mode").escape("SMOD?").eos().build(),
        CmdBuilder("get_trip_reset_mode").escape("TMOD?").eos().build(),
        CmdBuilder("get_stat_byte").escape("*STB?").eos().build(),
        # Error handling
        CmdBuilder("reset").escape("*RST").build(),
        CmdBuilder("clear_status").escape("*CLS").build(),
        CmdBuilder("get_error").escape("LERR?").eos().build(),
        CmdBuilder("clear_trip").escape("TCLR").eos().build(),
        # Setting values
        CmdBuilder("set_volt_ON").escape("HV").arg("OF|ON").eos().build(),
        CmdBuilder("set_trip_reset_mode").escape("TMOD ").int().build(),
        CmdBuilder("set_volt").escape("VSET ").float().eos().build(),
        CmdBuilder("set_volt_limit").escape("VLIM ").float().eos().build(),
        CmdBuilder("set_curr_limit").escape("ILIM ").float().escape("e").int().eos().build(),
        CmdBuilder("set_curr_trip").escape("ITRP ").float().escape("e").int().eos().build(),
    }

    in_terminator = "\n"
    out_terminator = "\n"

    def reset(self):
        """
        Resets the device.
        """
        self._device.reset()
        return "*RST"
        
    def clear_status(self):
        self._device.clear_status()
    
    def get_error(self):
        return self._device.error
        
    def clear_trip(self):
        self._device.trip = 0

    def get_idn(self):
        """
        Replies with the device's identity.
        """
        return self._device.idn

    def get_setting_mode(self):
        return self._device.setting_mode

    def set_volt_ON(self, value):
        volt_ON = 0
        if value == "ON": volt_ON = 1
        self._device.volt_ON = volt_ON

    def set_volt(self, value):
        self._device.volt = value
        return "Voltage set to: " + str(value)
        
    def get_volt(self):
        return self._device.volt
        
    def set_volt_limit(self, value):
        self._device.volt_limit = value
        return "Voltage limit set to: " + str(value)
        
    def get_volt_limit(self):
        return self._device.volt_limit
        
    def get_curr(self):
        return self._device.curr
        
    def get_curr_limit(self):
        return self._device.curr_limit

    def set_curr_limit(self, value, exponent):
        self._device.curr_limit = value * 10**exponent
        
    def get_curr_trip(self):
        return self._device.curr_trip

    def set_curr_trip(self, value, exponent):
        self._device.curr_trip = value * 10**exponent
        
    def set_trip_reset_mode(self, new_mode):
        self._device.trip_reset_mode = new_mode

    def get_trip_reset_mode(self):
        return self._device.trip_reset_mode
        
    def get_stat_byte(self):
        return self._device.stat_byte

    @has_log
    def handle_error(self, request, error):
        err = "An error occurred at request {}: {}".format(str(request), str(error))
        print(err)
        self.log.info(err)
        return str(err)
