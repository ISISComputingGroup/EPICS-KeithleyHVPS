##################################################
#
# Device simulator File
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


from collections import OrderedDict
from lewis.core.logging import has_log
from .states import DefaultState
from lewis.devices import StateMachineDevice
from random import randint
import time
import threading


@has_log
class SimulatedKeithley2290(StateMachineDevice):
    """
    Simulated Keithley2290 High-voltage power supply
    """

    def _initialize_data(self):
        """
        Initialize the device's attributes necessary for testing.
        """
        # Device name 
        self._idn = "KEITHLEY INSTRUMENTS, MODEL 2290-10 emulator"
        self._volt = 0.0
        self._volt_limit = 10000.0
        self._curr = 0.0
        self._curr_limit = 1050.0
        self._curr_trip = 1050.0
        self._trip_reset_mode = 0
        self._high_voltage_enable_switch = 1
        self._error = 0
        self._execution_error = 0
        # Bit 0 - Stable  - Indicates that the VSET or ILIM value is stable.
        # Bit 1 - V trip  - Indicates that a voltage trip has occurred.
        # Bit 2 - I trip  - Indicates that a current trip has occurred.
        # Bit 3 - I lim   - Indicates that a current limit condition has occurred.
        # Bit 4 - MAV     - Indicates message available in the GPIB output queue.
        # Bit 5 - ESB     - Indicates that an unmasked bit in the Standard Event Status Register has been set.
        # Bit 6 - RQS/MSS - Request for Service/Master Summary Status.
        # Bit 7 - HV on   - Indicates that the high voltage is on.
        self._stat_byte = 1
        self._error = 0
        
    def reset(self):
        self._initialize_data()
        
    def clear_status(self):
        self._stat_byte = 1
        
    @property
    def idn(self):
        return self._idn
        
    @property
    def error(self):
        return self._error
        
    @property
    def volt(self):
        return self._volt
        
    def volt_external(self, new_volt):
        """ Used by Lewis backdoor """
        if new_volt > self._volt_limit:
            new_volt = 0
            self._stat_byte |= (1 << 1)
            self._stat_byte |= (1 << 5) # Set ESB bit
        else:
            self._stat_byte &= ~(1 << 1)
            
        self._volt = new_volt
       
    @volt.setter
    def volt(self, new_volt):
        if new_volt > self.volt_limit:
            self._execution_error = 1
            self._error = 10
        else:
            self._volt = new_volt
            
    @property
    def stable_bit(self):
        return (self._stat_byte >> 0) & 1 # Reading the register does not cause it to be cleared
            
    @property
    def esb_alert_bit(self):
        _esb_alert_bit = (self._stat_byte >> 5) & 1
        self._stat_byte &= ~(1 << 5) # Reading the register causes it to be cleared
        return _esb_alert_bit
        
    @property
    def MSS_bit(self):
        _MSS_bit = (self._stat_byte >> 6) & 1
        self._stat_byte &= ~(1 << 6) # Reading the register causes it to be cleared
        return _MSS_bit
        
    @property
    def volt_on_bit(self):
        return (self._stat_byte >> 7) & 1 # Reading the register does not cause it to be cleared
        
    @property
    def high_voltage_enable_switch(self):
        return self._high_voltage_enable_switch
        
    @high_voltage_enable_switch.setter
    def high_voltage_enable_switch(self, enable):
        self._high_voltage_enable_switch = enable
        
    @property
    def execution_error(self):
        old_execution_error = self._execution_error
        self._execution_error = 0 # Reading the register causes it to be cleared
        return old_execution_error
        
    @property
    def error(self):
        old_error = self._error
        self._error = 0 # Reading the register causes it to be cleared
        return old_error
        
    @property
    def volt_ON(self):
        return (self._stat_byte >> 7) & 1
        
    @volt_ON.setter
    def volt_ON(self, new_volt_ON):
        if new_volt_ON and not self._high_voltage_enable_switch:
            self._execution_error = 1
            self._error = 10            # Execution error
            self._stat_byte |= (1 << 6) # Set MSS bit
            return
            
        if new_volt_ON:
            self._stat_byte |= (1 << 7)
        else:
            self._stat_byte &= ~(1 << 7)
        
    @property
    def volt_limit(self):
        return self._volt_limit
        
    @volt_limit.setter
    def volt_limit(self, new_volt_limit):
        if self._volt > self._volt_limit:
            self._execution_error = 1
            self._error = 10
        else:
            self._volt_limit = new_volt_limit
    
    @property
    def curr(self):
        if (self._stat_byte & (1 << 3)) != 0:
            self._stat_byte |= (1 << 5) # Set ESB bit
            return self._curr_limit
        else:
            return self._curr
    
    @curr.setter
    def curr(self, new_curr):
        if new_curr > self._curr_trip:
            new_curr = 0
            self._stat_byte |= (1 << 2)
            self._stat_byte |= (1 << 5) # Set ESB bit
        else:
            self._stat_byte &= ~(1 << 2)
            
        if new_curr > self._curr_limit:
            self._stat_byte |= (1 << 3)
            self._stat_byte |= (1 << 5) # Set ESB bit
            new_curr = self._curr_limit
        else:
            self._stat_byte &= ~(1 << 3)
        self._curr = new_curr
        
    @property
    def curr_trip(self):
        return self._curr_trip
        
    @curr_trip.setter
    def curr_trip(self, new_curr_trip):
        self._curr_trip = new_curr_trip
        if self._curr > self._curr_trip:
            self._curr = 0
            self._stat_byte |= (1 << 2)
            self._stat_byte |= (1 << 5) # Set ESB bit
        else:
            self._stat_byte &= ~(1 << 2)
    
    @property
    def curr_limit(self):
        return self._curr_limit
        
    @curr_limit.setter
    def curr_limit(self, new_curr_limit):
        self._curr_limit = new_curr_limit
        if self._curr > self._curr_limit:
            self._stat_byte |= (1 << 3)
            self._curr = new_curr_limit
        else:
            self._stat_byte &= ~(1 << 3)
        
    @property
    def trip_reset_mode(self):
        return self._trip_reset_mode
        
    @trip_reset_mode.setter
    def trip_reset_mode(self, new_trip_reset_mode):
        self._trip_reset_mode = new_trip_reset_mode
    
    @property
    def stat_byte(self):
        return self._stat_byte

    @property
    def trip(self):
        return (self._stat_byte & 6) != 0
        
    @trip.setter
    def trip(self, new_trip):
        if new_trip != 0:
            self._stat_byte |= 6
        else:
            self._stat_byte &= ~6

    def _get_state_handlers(self):
        """
        Returns: states and their names
        """
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """
        Returns: the name of the initial state
        """
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """
        Returns: the state transitions
        """
        return OrderedDict()
