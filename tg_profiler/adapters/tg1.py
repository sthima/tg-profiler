# encoding: utf-8

"""TurboGears automatic startup/shutdown extension."""


from turbogears.config import config
from tg_profiler.control import interface


__all__ = ['start_extension', 'shutdown_extension']



def start_extension():
    # interface.start will exit immediately if tg_profiler is not enabled.
    interface.start(config)

def shutdown_extension():
    interface.stop()
