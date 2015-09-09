#condig=utf-8

from __future__ import with_statement

import os
import gc
import csv
import sys
import shutil
from tempfile import NamedTemporaryFile
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

    def __init__(self, log_path, **options):
        super(MemorySnapshotProfiler, self).__init__()
        print options
        self.options = options
        self.log_path = log_path

        self.file_prefix = self.options.get("file_prefix", "tg_profiler.")
        self.file_suffix = self.options.get("file_suffix", ".csv")
        self.interval = self.options.get("interval", 60)
        self.rotation = self.options.get("rotation", 10)
        self.max_execution_time = self.options.get("max_execution_time", 0)
        self.execution_sleep  = self.options.get("execution_sleep ", self.interval/4)

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
        while self.rotation and len(self.saved_logs) >= self.rotation:
            log.debug("Log rotation threshold achieved, let's remove ")
            os.remove(self.saved_logs.pop(0))
        log_filename = "tg_profiler.%s.csv"%datetime.now().strftime("%Y-%m-%dT%H:%M")
        log_file_path = os.path.join(self.log_path, log_filename)
        self.saved_logs.append(log_file_path)
        return log_file_path

    def profile_and_save(self):
        """ Method responsible for taking the snapshot. It will retrieve all
        variables from the Garbage Collector module, will filter by those who can
        be analyzed, then it will calculate the size of every variable and will
        save them in the profile file.
        """
        if gc.garbage:
            log.error("Found %d garbage objects"%len(gc.garbage))
        with NamedTemporaryFile("w", suffix=".csv", delete=False) as log_file:
            objects = self.get_objects()
            log_writer = csv.writer(log_file)
            log_writer.writerow([
                "File",
                "Object Name",
                "Object Type",
                "Size",
            ])
            if self.max_execution_time > 0:
                last_cycle = time()
                for obj in objects:
                    try:
                        if time() - last_cycle >= self.max_execution_time:
                            log.info("Taking more time than expected, will "
                                     "sleep for %s seconds"%self.execution_sleep)
                            sleep(self.execution_sleep)
                            last_cycle = time()
                        self.save_obj_to_file(obj, log_writer)
                    except Exception, e:
                        log.error(e)
            else:
                for obj in objects:
                    try:
                        self.save_obj_to_file(obj, log_writer)
                    except Exception, e:
                        log.error(e)
            shutil.move(log_file.name, self.log_file())

    def get_objects(self):
        """ Get all objects that are visible by the Garbage Collector, and filters
        them by those which size can be calculated.

        :returns list: List with all objects visible by the Garbage Collector which
            size can be calculated.
        """
        objects = gc.get_objects()
        log.debug("%d objects found"%len(objects))
        objects = filter(lambda r: hasattr(r, "__sizeof__"), objects)
        log.debug("%d __sizeof__ filtered objects found"%len(objects))

        return objects

    def save_obj_to_file(self, obj, csvfile):
        """ Saves object data to CSV file """
        size = sys.getsizeof(obj)
        csvfile.writerow([
            getattr(obj, __file__, "unknown"),
            getattr(obj, __name__, "annonymous"),
            type(obj),
            size,
        ])

    def run(self):
        """ Implementation of the `threading.Thread.run` method, which will run
        when someone starts this Thread.
        """
        self.running = True
        while self.running:
            try:
                log.debug("Trying to profile the application")
                l = time()
                self.profile_and_save()
                log.debug("Took %d seconds"%(time()-l))
                log.debug("Profiled successfully, waiting until next time")
            except Exception, e:
                log.error(e)
            finally:
                sleep(self.interval)

    def stop(self, ):
        """ Method responsible for stopping this thread's main loop """
        self.running = False

