#condig=utf-8

from __future__ import with_statement

import gc
import csv
import threading

from tg_adapter.sizeof import asized

class TGProfiler(threading.Thread):

    def __init__(self, log_path, interval=60, rotation=10):
           self.log_path = log_path
           self.interval = interval
           self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                objects = gc.get_objects()
                with open(self.log_file()) as log_file:
                    log_writer = csv.writer(log_file)
                    log_writer.writerow(["File", "Object Name", "Object Type", "Flat Size", "Total Size"])
                    for obj in objects:
                        obj_file = "unknown"
                        if hasattr(obj, "__file__"):
                            obj_file = obj.__file__
                        asized_obj = asized(obj)

                        log_writer.writerow([obj_file, asized_obj.name, type(obj), asized_obj.flat, asized_obj.total])
            except:
                pass

    def stop(self, ):
        self.running = False


