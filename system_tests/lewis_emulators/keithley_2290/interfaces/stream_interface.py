from lewis.adapters.stream import StreamInterface, Cmd
from ..control_modes import OutputMode
from lewis.core.logging import has_log

from lewis.utils.command_builder import CmdBuilder

@has_log
class Keithley2290StreamInterface(StreamInterface):

    # Commands that we expect via serial during normal operation
    serial_commands = {
        # readback values
        CmdBuilder("get_voltage").escape("VOUT?").build(),
        CmdBuilder("get_current").escape("IOUT?").build(),
        CmdBuilder("reset").escape("*RST").build(),
        CmdBuilder("clear_trip").esacpe("TCLR").build(),
        CmdBuilder("identify").escape("*IDN?").build(),
        # Error handling
        CmdBuilder("get_error").escape("LERR?").eos().build()
        CmdBuilder("setting_mode").escape("SMOD?").build(),
        CmdBuilder("set_HV_ON").escape("HVON").build(),   
        CmdBuilder("set_HV_OFF").escape("HVOF").build(),   
        CmdBuilder("get_trip_reset_mode").escape("TMOD?").build(),
        CmdBuilder("set_trip_reset_mode").escape("TMOD ").int().build(),
        CmdBuilder("get_voltage_limit").escape("VLIM?").build(),
    }

    # Private control commands that can be used as an alternative to the lewis backdoor
    control_commands = {
        Cmd("set_voltage", "^\VSET\s([-+]?[0-9]*\.?[0-9]+)$"),
        Cmd("set_voltage_limit", "^\VLIM\s([-+]?[0-9]*\.?[0-9]+)$"),
        Cmd("set_current_limit", "^\ILIM\s([-+]?[0-9]*\.?[0-9]+)$"),
        Cmd("set_current_trip", "^\ITRP\s([-+]?[0-9]*\.?[0-9]+)$"),
    }

    commands = set.union(serial_commands, control_commands)

    in_terminator = "\n"
    out_terminator = "\n"

    def get_values(self):
        """
        Get the current and voltage readings

        :return: A string of 2 doubles: voltage, current. In that order
        """
        return ", ".join([
            self._device.get_voltage(as_string=True),
            self._device.get_current(as_string=True),
        ]) if self._device.get_output_mode() == OutputMode.ON else None

    def reset(self):
        """
        Resets the device.
        """
        self._device.reset()
        return "*RST"

    def identify(self):
        """
        Replies with the device's identity.
        """
        return "Keithley 2290 10 kV Power Supply"

    def set_voltage(self, value):
        self._device.voltage = float(value)
        return "Voltage set to: " + str(value)
        
    def get_voltage(self, value):
        return self._device.voltage
        
    def set_voltage_limit(self, value):
        self._device.voltage_limit = float(value)
        return "Voltage limit set to: " + str(value)
        
    def get_voltage_limit(self):
        return self._device.voltage_limit

    def set_trip_reset_mode(self, new_mode):
        return self._device.trip_reset_mode = new_mode

    def trip_reset_mode(self):
        return self._device.trip_reset_mode

    @has_log
    def handle_error(self, request, error):
        err = "An error occurred at request {}: {}".format(str(request), str(error))
        print(err)
        self.log.info(err)
        return str(err)
