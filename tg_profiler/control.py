# encoding: utf-8

"""tg_profiler startup and shutdown interface.
"""


import logging
from tg_profiler.profilers.memory_snapshot import MemorySnapshotProfiler

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

        self.start_profilers()

        log.info("tg_profiler extension started successfully.")

    def start_profilers(self, ):
        """ Start all profilers and register them at `self.profilers`
        """

        self.profilers = []
        if self.config.get("tg_profiler.memory_snapshot.on", True):
            self.profiler = MemorySnapshotProfiler(
                self.config.get("tg_profiler.log_path", "tg_profiler/memory_snapshot"),
                **self.profiler_options("memory_snapshot")
            )
            self.profiler.start()

    def profiler_options(self, profiler):
        """ Get all options to `profiler` defined in self.config

        :param str profiler: Profiler name, as used in the TurboGears configuration
            file.
        :returns dict: Dictionary with all options defined to `profiler`.
        """
        key_prefix = "tg_profiler.%s."%profiler
        keys = self.config.configs.get("global").keys()
        profiler_keys = filter(lambda key: key.startswith(key_prefix), keys)
        options = {}
        for key in profiler_keys:
            options[key.replace(key_prefix, "")] = self.config.get(key)

        return options

    def stop(self, force=False):
        if not self.config.get("tg_profiler.on", False) or (not self.profiler.running and not force):
            return
        log.info("tg_profiler extension shutting down.")

        for profiler in self.profilers:
            profiler.running = False

interface = ControlClass()
