import serial
import os
import subprocess
import time

COM_ID = 0
DEVICE_MAC = "20:14:03:24:26:84"

#cmd = "/usr/bin/rfcomm connect %s %s" % (COM_ID, DEVICE_MAC)
#subprocess.Popen(cmd, shell=True)
#time.sleep(3)

while(True):
    try:
        os.system("rfkill unblock bluetooth")
        os.system("killall rfcomm")
        cmd = "/usr/bin/rfcomm connect %s %s" % (COM_ID, DEVICE_MAC)
        subprocess.Popen(cmd, shell=True)
        time.sleep(3)
        bluetoothSerial = serial.Serial("/dev/rfcomm0", 38400)
        break
    except Exception, ex:
        pass

bluetoothSerial.write("stp\n")
