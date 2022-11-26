import time
import unittest

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir, IOCRegister
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, skip_if_recsim, unstable_test

DEVICE_PREFIX = "KHLY2290_01"

IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("KHLY2290"),
        "macros": {},
        "emulator": "keithley_2290",
    },
]

TEST_MODES = [TestModes.RECSIM, TestModes.DEVSIM]

on_off_status = {False: "OFF", True: "ON"}

def _insert_reading(class_object, reading):
    class_object._lewis.backdoor_run_function_on_device("insert_mock_data", [reading])
    time.sleep(0.5)  # for synchronicity help


class Status(object):
    ON = "ON"
    OFF = "OFF"


class Keithley2290DeviceTests(unittest.TestCase):
    """
    Tests for the Keithley2290.
    """

    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("keithley_2290", DEVICE_PREFIX)
        self.ca = ChannelAccess(default_timeout=30, device_prefix=DEVICE_PREFIX, default_wait_time=0.0)
        self.ca.assert_that_pv_exists("IDN")
        self.ca.set_pv_value("RST", 1)
        self.ca.set_pv_value("CLS", 1)

    def test_WHEN_setting_volt_normally(self):
        volt_limit = 6000.0
        volt_setpoint = 5000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_limit, "VOLT_LIMIT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        self.ca.assert_setting_setpoint_sets_readback(volt_setpoint, "VOLT", expected_value=volt_setpoint, expected_alarm="NO_ALARM")

    @skip_if_recsim("Test does not work with mbbiDirect")
    def test_WHEN_setting_volt_ON(self):
        on = "ON"
        self.ca.assert_setting_setpoint_sets_readback(on, "VOLT_ON", expected_value=on, expected_alarm="NO_ALARM")
        
    @skip_if_recsim("Test does not work with mbbiDirect")
    def test_WHEN_setting_volt_OFF(self):
        off = "OFF"
        self.ca.assert_setting_setpoint_sets_readback(off, "VOLT_ON", expected_value=off, expected_alarm="NO_ALARM")
        
    def test_WHEN_setting_trip_reset_mode(self):
        Automatic = "Automatic"
        self.ca.assert_setting_setpoint_sets_readback(Automatic, "TRIP_RESET_MODE", expected_value=Automatic, expected_alarm="NO_ALARM")
        
    @skip_if_recsim("no volt_limit side effect recsim")
    def test_WHEN_setting_volt_beyond_limit(self):
        volt_limit = 4000.0
        volt_setpoint = 5000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_limit, "VOLT_LIMIT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        self.ca.assert_setting_setpoint_sets_readback(volt_setpoint, "VOLT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        
    @skip_if_recsim("no backdoor in recsim")
    def test_WHEN_setting_curr_beyond_limit(self):
        curr_limit = 1E-7
        curr_actual = 1E-6
        self.ca.assert_setting_setpoint_sets_readback(curr_limit, "CURR_LIMIT", expected_value=curr_limit, expected_alarm="NO_ALARM")
        self._lewis.backdoor_set_on_device("curr", curr_actual)
        self.ca.assert_that_pv_is("CURR", curr_limit)
        self.ca.assert_that_pv_is("CURR_LIMITED", "LIMITED")
        
    @skip_if_recsim("no backdoor in recsim")
    def test_WHEN_setting_curr_beyond_trip(self):
        curr_trip = 1E-6
        curr_actual = 2E-6
        self.ca.assert_setting_setpoint_sets_readback(curr_trip, "CURR_TRIP", expected_value=curr_trip, expected_alarm="NO_ALARM")
        self._lewis.backdoor_set_on_device("curr", curr_actual)
        self.ca.assert_that_pv_is("CURR", 0)
        self.ca.assert_that_pv_alarm_is("CURR_TRIPPED", self.ca.Alarms.MAJOR)
        self.ca.set_pv_value("CLT", 1)
        self.ca.assert_that_pv_alarm_is("CURR_TRIPPED", self.ca.Alarms.NONE)

