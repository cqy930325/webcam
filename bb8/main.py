# -*- coding: utf-8 -*-
__author__ = 'gjerryfe'


import httpserver
import serialdevice
import time
import threading
from log import logger

if __name__ == "__main__":
    threads = []

    httpServer = threading.Thread(target=httpserver.run, args=())
    threads.append(httpServer)

    #sppServer = threading.Thread(target=sppserver.run, args=())
    #threads.append(sppServer)

    #serialDevice = serialdevice.SerialDevice()


    for t in threads:
        t.setDaemon(True)
        t.start()

    logger.debug("service running")

    while True:
        time.sleep(1)