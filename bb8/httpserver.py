# -*- coding: utf-8 -*-
__author__ = 'gjerryfe'

import os
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import json
import sys
import socket
import command
from serialdevice import SerialDevice as Device
from log import logger
import shutil

class WebAPIRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        file_path = "statics" + self.path
        if not os.path.exists(file_path):
            self.wfile.write("file not found")
            self.send_response(404)
            return

        with open(file_path) as fp:
            shutil.copyfileobj(fp, self.wfile)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        #logger.debug(data)
        if self.path == "/pose":
            pos = json.loads(data);
            good = int(pos['good'])
            print good
            sys.stdout.flush()
            cmd = command.Command()
            if int(pos['good']) == 1:
                print pos['y'],pos['z'],pos['yaw']
                sys.stdout.flush()
                yaw = float(pos['yaw'])
                x = float(pos['y'])
                y = float(pos['z'])
                cmd.to_Cmd(yaw,x,y)
            elif good == 2:
                x = float(pos['y'])
                y = float(pos['z'])
                sys.stdout.flush()
                self.send_response(200)
                self.end_headers()
                return
            else:
                stop = json.dumps({"stop":""})
                cmd.load_json(stop)
            self.send_response(200)
            self.end_headers()
            while (not hasattr(self, "device")):
                try:
                    self.device = Device()
                except:
                    pass
            try:
                # device = Device()
                res = self.device.send(cmd)
                self.wfile.write(res.to_json())
            except Exception, e:
                self.wfile.write(json.dumps({"status":"ERROR",
                                             "msg": e.message}))
        else:
            try:
                print data
                sys.stdout.flush()
                cmd = command.Command()
                cmd.load_json(data)
            except command.InvalidCommand:
                self.wfile.write(json.dumps({"status":"ERROR", "msg":"invalid cmd"}))
                return
            self.send_response(200)
            self.end_headers()
            #self.wfile.write(data)
            while (not hasattr(self, "device")):
                try:
                    self.device = Device()
                except:
                    pass
            try:
                # device = Device()
                res = self.device.send(cmd)
                self.wfile.write(res.to_json())
            except Exception, e:
                self.wfile.write(json.dumps({"status":"ERROR",
                                             "msg": e.message}))



def run():
    server = HTTPServer(("", 8000), WebAPIRequestHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    server.serve_forever()
