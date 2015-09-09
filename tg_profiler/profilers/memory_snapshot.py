#condig=utf-8

from __future__ import with_statement

import os
import gc
import csv
import sys
import logging
from time import sleep, time
import threading
from datetime import datetime

log = logging.getLogger(__name__)

class MemorySnapshotProfiler(threading.Thread):
    """ Profiler responsible for taking a snapshot of (sort of) all objects
    reachable by the Garbage Collector. It will take a snapshot every `interval`
    seconds, and will keep only the last `rotation` files. The snapshot is saved
    as a CSV file, to be analyzed later. This can help you to find memory leaks
    in your application.

    :param str log_path: Path where all the profile files will be saved.
    :param int interval: Interval, in seconds, which the profiler will wait
        between every snapshot.
    :param int rotation: Number of files to keep before starting to delete the
        oldest one.
    """

    def __init__(self, log_path, interval=60, rotation=10):
        super(MemorySnapshotProfiler, self).__init__()
        self.log_path = log_path
        self.interval = interval
        self.rotation = rotation
        self.running = False
        self.saved_logs = []

    def log_file(self, ):
        """ Method responsible for retireving the next profile file path.

        :return str: Path to save the next profile file.
        """
        if not os.path.exists(self.log_path):
            log.debug("Path %s doesn't exist, so let's create it"%self.log_path)
            os.makedirs(self.log_path)
            log.debug("Path %s created successfully"%self.log_path)
        while len(self.saved_logs) >= self.rotation:
            log.debug("Log rotation threshold achieved, let's remove ")
            os.remove(self.saved_logs.pop(0))
        log_filename = "tg_profiler.%s.csv"%datetime.now().strftime("%Y-%m-%dT%H:%M")
        log_file_path = os.path.join(self.log_path, log_filename)
        self.saved_logs.append(log_file_path)
        return log_file_path

    def profile_and_log(self):
        """ Method responsible for taking the snapshot. It will retrieve all
        variables from the Garbage Collector module, will filter by those who can
        be analyzed, then it will calculate the size of every variable and will
        save them in the profile file.
        """
        objects = gc.get_objects()
        log.info("Found %d garbage objects"%len(gc.garbage))
        with open(self.log_file(), 'w') as log_file:
            log.debug("%d objects found"%len(objects))
            objects = filter(lambda r: hasattr(r, "__sizeof__"), objects)
            log.debug("%d __sizeof__ filtered objects found"%len(objects))
            objects = filter(lambda r: hasattr(r, "__name__"), objects)
            log.debug("%d __name__ filtered objects found"%len(objects))
            objects = filter(lambda r: hasattr(r, "__file__"), objects)
            log.debug("%d __file__ filtered objects found"%len(objects))
            log_writer = csv.writer(log_file)
            log_writer.writerow([
                "File",
                "Object Name",
                "Object Type",
                "Size"
            ])
            for obj in objects:
                try:
                    obj_file = "unknown"
                    if hasattr(obj, "__file__"):
                        obj_file = obj.__file__
                    size = sys.getsizeof(obj)
                    log_writer.writerow([
                        obj_file,
                        obj.__name__,
                        type(obj),
                        size
                    ])
                except Exception, e:
                    log.error(e)

    def run(self):
        """ Implementation of the `threading.Thread.run` method, which will run
        when someone starts this Thread.
        """
        self.running = True
        while self.running:
            try:
                log.debug("Trying to profile the application")
                l = time()
                self.profile_and_log()
                log.debug("Took %d seconds"%(time()-l))
                log.debug("Profiled successfully, waiting until next time")
            except Exception, e:
                log.error(e)
            finally:
                sleep(self.interval)

    def stop(self, ):
        """ Method responsible for stopping this thread's main loop """
        self.running = False

