TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# build an ioc application

PROD_IOC = Keithley2290Test

# Keithley2290Test.dbd will be made up from these files:
Keithley2290Test_DBD += base.dbd
#include definitions for any other support applications needed
Keithley2290Test_DBD += devKeithley2290.dbd
Keithley2290Test_DBD += drvAsynSerialPort.dbd
Keithley2290Test_DBD += asynRecord.dbd

# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
Keithley2290Test_SRCS += Keithley2290Test_registerRecordDeviceDriver.cpp
Keithley2290Test_SRCS_DEFAULT += Keithley2290TestMain.cpp

#add a definition for each support application used by this application
#Keithley2290Test_LIBS += devKeithley2290 asyn
Keithley2290Test_LIBS += asyn


#NOTES:
#      1)It is not possible to build sncExample both as a component of Keithley2290Test
#        and standalone. You must choose only one.
#      2)To build sncExample SNCSEQ must be defined in <top>/configure/RELEASE

#The following builds sncExample as a component of Keithley2290Test
#Keithley2290Test_SRCS += sncExample.stt
#Keithley2290Test_LIBS += seq pv

Keithley2290Test_LIBS += $(EPICS_BASE_IOC_LIBS)

#The following builds sncExample as a standalone application
#PROD_HOST += sncExample
#sncExample_SNCFLAGS += +m
#sncExample_SRCS += sncExample.stt
#sncExample_LIBS += seq pv
#sncExample_LIBS += $(EPICS_BASE_HOST_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

