# encoding: utf-8

"""tg_profiler startup and shutdown interface.
"""


import logging

log = logging.getLogger(__name__)

class ControlClass(object):
    """Control tg_profiler startup and shutdown."""

    def __init__(self):
        self.running = False
        self.config = dict()

    def start(self, config, extra_classes=None):
        self.config = config
        if not self.config.get("tg_profiler.on", False):
            return

        log.info("tg_profiler extension starting up.")

    def stop(self, force=False):
        if not self.running and not force:
            return
        log.info("tg_profiler extension shutting down.")

        self.running = False

interface = ControlClass()
