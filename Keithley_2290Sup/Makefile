TOP=..
include $(TOP)/configure/CONFIG
#=======================================

# Install .dbd and .db files

# Keithley 2290 Library 
LIBRARY_IOC += Keithley2290
DATA += devKeithley2290.proto
DBD += devKeithley2290.dbd

DB += devKeithley2290.db

Keithley2290_LIBS += asyn stream
Keithley2290_LIBS += $(EPICS_BASE_IOC_LIBS)

#=======================================
include $(TOP)/configure/RULES
