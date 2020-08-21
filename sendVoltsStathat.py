import RPi.GPIO as gpio
import smbus
import time
import sys
import struct
from datetime import datetime
from stathat import StatHat
from rvmonitorVars import *

stathat = StatHat()

bus = smbus.SMBus(1)

# calculation to get voltage from analog reading
# voltageMultiplier = 1023/5/3.10 
# new value 2020-08-21 based on volt meter readings
voltageMultiplier = 67.59
print("Using voltage multiplier: " + str(voltageMultiplier))

address = 0x04
def main():
    print(str(datetime.now()) + " Starting up...")
    status = False
    runTimes = 1

    while runTimes > 0:
        status = not status
        bus.write_byte(address, 1 if status else 0)
        time.sleep(3)
#        print(bus.read_byte(address))
        arduinoData = (bus.read_i2c_block_data(address, 0, 32)) # read 32 chars 
#        print(arduinoData);
#        print("".join(map(chr, arduinoData)))
        teensyData = ("".join(map(chr, arduinoData)))
#        print(teensyData.strip())
#        print(teensyData)
        voltsStart   = teensyData.find("Volts:",0)
        voltsEnd     = teensyData.find(":",voltsStart) + 1
        voltsDataEnd = teensyData.find("|",voltsStart+6)
        voltsVal     = teensyData[voltsEnd:voltsDataEnd]
        print(str(datetime.now()) + " " + "Teensey Volts: " +  voltsVal)

        analogStart   = teensyData.find("RawAnalog:",0)
        analogEnd     = teensyData.find(":",analogStart) + 1
        analogDataEnd = teensyData.find("|",analogStart+10)
        analogVal     = teensyData[analogEnd:analogDataEnd]
        print(str(datetime.now()) + " " + "RawAnalog: " + analogVal)

        adjustedVoltsVal = float(analogVal) / voltageMultiplier
        adjustedVoltsVal = str(adjustedVoltsVal)
        print(str(datetime.now()) + " " + "Adjusted Volts: " + adjustedVoltsVal)

        print("Sending to stathat: " + adjustedVoltsVal)
        stathat.ez_post_value(stathatKey, 'rv.volts', adjustedVoltsVal)
        stathat.ez_post_value(stathatKey, 'rv.analogVolts', analogVal)

        time.sleep(60)

        runTimes = (runTimes - 1)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        gpio.cleanup()
        sys.exit(0)
