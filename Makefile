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

define DIR_template
 $(1)_DEPEND_DIRS = configure
endef
$(foreach dir, $(filter-out configure,$(DIRS)),$(eval $(call DIR_template,$(dir))))

## if you have any TestApp type directories the you need
## to add a dependency here on e.g. the Sup directory
Keithley_2290TestApp_DEPEND_DIRS += Keithley_2290Sup

include $(TOP)/configure/RULES_TOP

ioctests:
	.\system_tests\run_tests.bat
