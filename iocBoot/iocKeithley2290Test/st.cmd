#!../../bin/linux-x86_64/Keithley2290Test

## You may have to change Keithley2290Test to something else
## everywhere it appears in this file

< envPaths

epicsEnvSet "STREAM_PROTOCOL_PATH" "${TOP}/data"

cd ${TOP}

## Register all support components
dbLoadDatabase("dbd/Keithley2290Test.dbd",0,0)
Keithley2290Test_registerRecordDeviceDriver(pdbbase)

#The following commands are for a local serial line
drvAsynSerialPortConfigure("L0","COM2",0,0,0)
asynSetOption("L0", -1, "baud", "9600")
asynSetOption("L0", -1, "bits", "8")
asynSetOption("L0", -1, "parity", "none")
asynSetOption("L0", -1, "stop", "1")
asynSetOption("L0", -1, "clocal", "Y")
asynSetOption("L0", -1, "crtscts", "N")
asynOctetSetInputEos("L0", -1, "\n")
asynOctetSetOutputEos("L0", -1, "\n")

asynSetTraceFile("L0",-1,"")
#asynSetTraceMask("L0",-1,0x09)
asynSetTraceIOMask("L0",-1,0x2)

## Load record instances
dbLoadRecords("db/devKeithley2290.db","P=KHLY2290:,PORT=L0")

cd ${TOP}/iocBoot/${IOC}
iocInit()

## Start any sequence programs
#seq sncxxx,"user=afpHost"
