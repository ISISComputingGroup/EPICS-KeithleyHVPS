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


class SetUpTests(unittest.TestCase):
    """
    Tests for the Keithley2290.
    """

    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("keithley_2290", DEVICE_PREFIX)
        self.ca = ChannelAccess(default_timeout=30, device_prefix=DEVICE_PREFIX, default_wait_time=0.0)
        self.ca.assert_that_pv_exists("IDN")
            
    def test_WHEN_setting_volt_normally(self):
        volt_limit = 6000.0
        volt_setpoint = 5000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_limit, "VOLT_LIMIT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        self.ca.assert_setting_setpoint_sets_readback(volt_setpoint, "VOLT", expected_value=volt_setpoint, expected_alarm="NO_ALARM")

    def test_WHEN_setting_volt_ON(self):
        on = "ON"
        self.ca.assert_setting_setpoint_sets_readback(on, "VOLT_ON", expected_value=on, expected_alarm="NO_ALARM")
        
    def test_WHEN_setting_volt_OFF(self):
        off = "OFF"
        self.ca.assert_setting_setpoint_sets_readback(off, "VOLT_ON", expected_value=off, expected_alarm="NO_ALARM")

    def test_WHEN_setting_volt_beyond_limit(self):
        volt_limit = 4000.0
        volt_setpoint = 5000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_limit, "VOLT_LIMIT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        self.ca.assert_setting_setpoint_sets_readback(volt_setpoint, "VOLT", expected_value=volt_limit, expected_alarm="MINOR")

