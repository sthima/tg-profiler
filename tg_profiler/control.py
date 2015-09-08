# encoding: utf-8

"""tg_profiler startup and shutdown interface.
"""


import logging
from tg_profiler import TGProfiler

log = logging.getLogger(__name__)

class ControlClass(object):
    """Control tg_profiler startup and shutdown."""

    def __init__(self):
        self.config = dict()

    def start(self, config, extra_classes=None):
        self.config = config
        if not self.config.get("tg_profiler.on", False):
            return

        log.info("tg_profiler extension starting up.")

        self.profiler = TGProfiler(
            self.config.get("tg_profiler.log_path", "/var/log/tg_profiler/"),
            self.config.get("tg_profiler.interval", 60),
            self.config.get("tg_profiler.rotation", 10)
        )
        self.profiler.start()

        log.info("tg_profiler extension started successfully.")

    def stop(self, force=False):
        if not self.config.get("tg_profiler.on", False) or (not self.profiler.running and not force):
            return
        log.info("tg_profiler extension shutting down.")

        self.profiler.running = False

interface = ControlClass()
