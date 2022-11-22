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
        self._trip_reset_mode = 0
        self._trip = 0
        self._stat_byte = 0
        self._error = 0
        
    @property
    def idn(self):
        return self._idn
        
    @property
    def volt(self):
        return self._volt
        
    @volt.setter
    def volt(self, new_volt):
        if new_volt > self.volt_limit:
            new_volt = self.volt_limit
        self._volt = new_volt
        
    @property
    def volt_ON(self):
        return (self._status_byte >> 7) & 1
        
    @volt_ON.setter
    def volt_ON(self, new_volt_ON):
        self._status_byte |= new_volt_ON
        
    @property
    def volt_limit(self):
        return self._volt_limit
        
    @volt_limit.setter
    def volt_limit(self, new_volt_limit):
        self._volt_limit = new_volt_limit
    
    @property
    def curr(self):
        return self._curr
    
    @curr.setter
    def curr(self, new_curr):
        self._curr = new_curr
        
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
