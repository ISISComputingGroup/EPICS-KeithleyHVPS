##################################################
#
# Device Test File
#
# Test file for Keithley 2290
# ISIS, November 2022
# Author : P.J. L. Heesterman (Capgemini Engineering)
#
# NOTES:
#
# 
#
##################################################

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

    def test_WHEN_setting_volt_ON_while_enabled(self):
        on = "ON"
        self.ca.set_pv_value("VOLT_ON:SP", on)
        self.ca.set_pv_value("STATUS.PROC", 1) # Force processing so we don't have to wait 1 second
        self.ca.assert_that_pv_is("VOLT_ON", on)
        
    @skip_if_recsim("no backdoor in recsim")
    def test_WHEN_setting_volt_ON_while_disabled(self):
        self._lewis.backdoor_set_on_device("high_voltage_enable_switch", 0)
        self.ca.assert_setting_setpoint_sets_readback("ON", "VOLT_ON", expected_value="OFF", expected_alarm="NO_ALARM")
        self.ca.set_pv_value("ERROR.PROC", 1)  # Force processing so we don't have to wait 1 second
        self.ca.assert_that_pv_is("EXECUTION_ERROR", "ERROR")
        self._lewis.backdoor_set_on_device("high_voltage_enable_switch", 1)
        self.ca.set_pv_value("EXECUTION_ERROR.PROC", 1) # Force processing to reset the fault condition
        self.ca.assert_that_pv_is("EXECUTION_ERROR", "OK")
        
    def test_WHEN_setting_volt_OFF(self):
        off = "OFF"
        self.ca.assert_setting_setpoint_sets_readback(off, "VOLT_ON", expected_value=off, expected_alarm="NO_ALARM")
        
    def test_WHEN_setting_trip_reset_mode(self):
        Automatic = "AUTO"
        self.ca.assert_setting_setpoint_sets_readback(Automatic, "TRIP_RESET_MODE", expected_value=Automatic, expected_alarm="NO_ALARM")
        
    @skip_if_recsim("no volt_limit side effect recsim")
    def test_WHEN_setting_volt_beyond_db_limit(self):
        volt_limit = 10000.0
        volt_setpoint = 11000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_setpoint, "VOLT", expected_value=volt_limit, expected_alarm="NO_ALARM")

    @skip_if_recsim("no backdoor in recsim")
    def test_WHEN_external_volt_beyond_volt_limit(self):
        volt_limit = 4000.0
        volt_external = 5000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_limit, "VOLT_LIMIT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        self._lewis.backdoor_set_on_device("volt_external", volt_external)
        self.ca.assert_that_pv_alarm_is("VOLT_TRIPPED", self.ca.Alarms.MAJOR)
        self.ca.set_pv_value("VOLT_TRIPPED_LATCHED", 0)
        self.ca.set_pv_value("VOLT_TRIPPED", 0)
        self.ca.set_pv_value("VOLT_ON:SP.PROC", 1)
        self.ca.set_pv_value("STATUS.PROC", 1) # Force processing so we don't have to wait 1 second
        self.ca.assert_that_pv_alarm_is("VOLT_TRIPPED", self.ca.Alarms.NONE)
        
    @skip_if_recsim("no volt_limit side effect recsim")
    def test_WHEN_setting_volt_beyond_volt_limit(self):
        volt_limit = 4000.0
        volt_setpoint = 5000.0
        self.ca.assert_setting_setpoint_sets_readback(volt_limit, "VOLT_LIMIT", expected_value=volt_limit, expected_alarm="NO_ALARM")
        self.ca.assert_setting_setpoint_sets_readback(volt_setpoint, "VOLT", expected_value=0, expected_alarm="NO_ALARM")
        self.ca.set_pv_value("ERROR.PROC", 1)  # Force processing so we don't have to wait 1 second
        self.ca.assert_that_pv_alarm_is("EXECUTION_ERROR", self.ca.Alarms.MAJOR)
        self.ca.set_pv_value("EXECUTION_ERROR.PROC", 1)
        self.ca.set_pv_value("STATUS.PROC", 1) # Force processing so we don't have to wait 1 second
        self.ca.assert_that_pv_alarm_is("VOLT_TRIPPED", self.ca.Alarms.NONE)

        
    @skip_if_recsim("no backdoor in recsim")
    def test_WHEN_setting_curr_beyond_limit(self):
        curr_limit = 100
        curr_actual = 1000
        self.ca.assert_setting_setpoint_sets_readback(curr_limit, "CURR_LIMIT", expected_value=curr_limit, expected_alarm="NO_ALARM")
        self._lewis.backdoor_set_on_device("curr", curr_actual)
        self.ca.assert_that_pv_is("CURR", curr_limit)
        self.ca.assert_that_pv_is("CURR_LIMITED", "LIMITED")
        
    @skip_if_recsim("no backdoor in recsim")
    def test_WHEN_setting_curr_beyond_trip(self):
        curr_trip = 1000
        curr_actual = 2000
        self.ca.assert_setting_setpoint_sets_readback(curr_trip, "CURR_TRIP", expected_value=curr_trip, expected_alarm="NO_ALARM")
        self._lewis.backdoor_set_on_device("curr", curr_actual)
        self.ca.assert_that_pv_is("CURR", 0)
        self.ca.assert_that_pv_alarm_is("CURR_TRIPPED", self.ca.Alarms.MAJOR)
        self.ca.set_pv_value("CLT", 1)
        self.ca.set_pv_value("CURR_TRIPPED_LATCHED", 0)
        self.ca.set_pv_value("CURR_TRIPPED", 0)
        self.ca.set_pv_value("VOLT_ON:SP.PROC", 1)
        self.ca.set_pv_value("STATUS.PROC", 1) # Force processing so we don't have to wait 1 second
        self.ca.assert_that_pv_alarm_is("CURR_TRIPPED", self.ca.Alarms.NONE)

