##################################################
#
# Stream Simulator File
#
# Simulator file for Keithley 2290
# ISIS, November 2022
# Author : P.J. L. Heesterman (Capgemini Engineering)
#
# NOTES:
#
#
#
##################################################

from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


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
        CmdBuilder("get_execution_error").escape("*ESR? 4").eos().build(),
        CmdBuilder("get_stable_bit").escape("*STB? 0").eos().build(),
        CmdBuilder("get_esb_alert_bit").escape("*STB? 5").eos().build(),
        CmdBuilder("get_volt_on_bit").escape("*STB? 7").eos().build(),
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
        CmdBuilder("set_curr_limit").escape("ILIM ").float().eos().build(),
        CmdBuilder("set_curr_trip").escape("ITRP ").float().eos().build(),
        CmdBuilder("set_service_request_enable").escape("*SRE ").int().eos().build(),
        CmdBuilder("set_event_status_enable").escape("ESE ").int().eos().build(),
    }

    in_terminator = "\n"
    out_terminator = "\n"

    @conditional_reply("connected")
    def reset(self):
        """
        Resets the device.
        """
        self._device.reset()

    @conditional_reply("connected")
    def clear_status(self):
        """
        Clears status flags.
        """
        self._device.clear_status()

    @conditional_reply("connected")
    def get_error(self):
        """
        Gets any error status.
        """
        return self._device.error

    @conditional_reply("connected")
    def clear_trip(self):
        """
        Clears any trip status.
        """
        self._device.trip = 0

    @conditional_reply("connected")
    def get_idn(self):
        """
        Replies with the device's identity.
        """
        return self._device.idn

    @conditional_reply("connected")
    def get_setting_mode(self):
        return self._device.setting_mode

    @conditional_reply("connected")
    def set_volt_ON(self, value):
        """
        Sets volt ON or OFF.
        """
        volt_ON = 0
        if value == "ON":
            volt_ON = 1
        self._device.volt_ON = volt_ON

    @conditional_reply("connected")
    def set_volt(self, value):
        """
        Sets requested voltage.
        """
        self._device.volt = value
        return "Voltage set to: " + str(value)

    @conditional_reply("connected")
    def get_volt(self):
        return self._device.volt

    @conditional_reply("connected")
    def set_volt_limit(self, value):
        """
        Sets requested voltage limit.
        """
        self._device.volt_limit = value
        return "Voltage limit set to: " + str(value)

    @conditional_reply("connected")
    def get_volt_limit(self):
        return self._device.volt_limit

    @conditional_reply("connected")
    def get_execution_error(self):
        return self._device.execution_error

    @conditional_reply("connected")
    def get_stable_bit(self):
        return self._device.stable_bit

    @conditional_reply("connected")
    def get_esb_alert_bit(self):
        return self._device.esb_alert_bit

    @conditional_reply("connected")
    def get_volt_on_bit(self):
        return self._device.volt_on_bit

    @conditional_reply("connected")
    def get_curr(self):
        return self._device.curr

    @conditional_reply("connected")
    def get_curr_limit(self):
        return self._device.curr_limit

    @conditional_reply("connected")
    def set_curr_limit(self, value):
        self._device.curr_limit = value

    @conditional_reply("connected")
    def get_curr_trip(self):
        return self._device.curr_trip

    @conditional_reply("connected")
    def set_curr_trip(self, value):
        """
        Sets the current trip value.
        """
        self._device.curr_trip = value

    @conditional_reply("connected")
    def set_trip_reset_mode(self, new_mode):
        """
        Sets the trip reset mode.
        """
        self._device.trip_reset_mode = new_mode

    @conditional_reply("connected")
    def get_trip_reset_mode(self):
        return self._device.trip_reset_mode

    @conditional_reply("connected")
    def get_stat_byte(self):
        """
        Gets the status byte value.
        """
        return self._device.stat_byte

    @conditional_reply("connected")
    def set_service_request_enable(self, new_SRE):
        # only stubbed here
        return

    @conditional_reply("connected")
    def set_event_status_enable(self, new_ESE):
        # only stubbed here
        return

    @has_log
    def handle_error(self, request, error):
        err = "An error occurred at request {}: {}".format(str(request), str(error))
        print(err)
        self.log.info(err)
        return str(err)
