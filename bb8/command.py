# -*- coding: utf-8 -*-
__author__ = 'gjerryfe'
import json

class InvalidCommand(Exception):
    pass

class Command():
    __valid_params = {
        "query" : "qry",
        "mov" : "",
        "pivot": "pvt",
        "stop": "stp",
        "tiltY": "tltY",
        "tiltZ": "tltZ",
		"thr" : "thr",
        "alpha": ""}
    cmd = {}
    def load_json(self, cmd):
        try:
            cmd = json.loads(cmd)
        except:
            raise InvalidCommand
        for key, value in cmd.items():
            if not key in self.__valid_params.keys():
                raise InvalidCommand
        self.cmd = cmd

    def to_string(self):
        if "query" in self.cmd.keys():
            return "".join(["qry" + "?" + v for k, v in self.cmd.items()])
        elif "pivot" in self.cmd.keys():
            return "pvt" + self.cmd["pivot"]
        elif "tiltZ" in self.cmd.keys():
            return "".join([self.__valid_params[k]+v for k,v in self.cmd.items()])
        elif "stop" in self.cmd.keys():
            return "".join([self.__valid_params[k]+v for k,v in self.cmd.items()])
	elif "mov" in self.cmd.keys():
	    return self.cmd["mov"] + self.cmd["alpha"] + "thr" + self.cmd["thr"]
        return ""

    def to_json(self):
        return json.dumps(self.cmd)

class Response():
    def load_string(self, res):
        self.res = res

    def to_json(self):
        return json.dumps(self.res)
