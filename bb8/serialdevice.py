
import os
import sys
import settings
import time

import socket
import subprocess
import serial
import command
import threading
from log import logger

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class Timeout(Exception):
    pass

class SerialDevice(Singleton):
    connected = False

    def __init__(self):
        if self.connected:
            return
        logger.debug(" serial device init")
        self.messages = {}
        self.com_id = settings.COM_ID
        self.device_mac = settings.DEVICE_MAC
        self.channel = settings.CHANNEL
        try:
            os.system("rfkill unblock bluetooth")
            os.system("killall rfcomm")
            cmd = "/usr/bin/rfcomm connect %s %s" % (self.com_id, self.device_mac)
            subprocess.Popen(cmd, shell=True)
            time.sleep(3)
            self.ser = serial.Serial("/dev/rfcomm0", 38400)
            t = threading.Thread(target=self.listen, args=())
            t.setDaemon(True)
            t.start()
            self.connected = True
        except Exception, e:
            logger.error("Connect device failed:" + e.message)
            raise Exception("Connect device failed")

    def listen(self):
        try:
            while True:
                data = self.ser.readline()
                data = data.strip()
                if settings.ASYNC:
                    self.messages[10000] = data
        except IOError:
            pass

    def send(self, cmd):
	logger.debug(cmd.to_string())
        self.ser.write(str(cmd.to_string()))
        self.ser.write("\n")
        if settings.ASYNC:
            message_id = 10000
            retries = 300
            while retries:
                retries = retries - 1
                if message_id in self.messages.keys():
                    res  = command.Response()
                    res.load_string(self.messages.pop(message_id))
                    return res
                time.sleep(0.01)
        raise Timeout("get result from serial time out!")


