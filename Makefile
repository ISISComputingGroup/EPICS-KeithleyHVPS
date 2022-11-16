# Makefile for Asyn Keithley_2290 support
#
# Created by zyz29835 on Mon Aug 14 09:53:15 2017
# Based on the Asyn streamSCPI template

TOP = .
include $(TOP)/configure/CONFIG

DIRS := configure
DIRS += $(wildcard *[Ss]up)
DIRS += $(wildcard *[Aa]pp)
DIRS += $(wildcard ioc[Bb]oot)

include $(TOP)/configure/RULES_TOP

ioctests:
	.\system_tests\run_tests.bat
