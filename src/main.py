import sync_timer
import config
import binance_wrapper
import firefly_wrapper
from threading import Event
from threading import Thread


def start():
    if not binance_wrapper.connect():
        exit(-11)
    if not firefly_wrapper.connect():
        exit(-12)

    sync_timer.initial_sync()

    print('Starting Sync Thread\n')
    stopFlag = Event()
    thread = MyThread(stopFlag)
    thread.start()

    # this will stop the timer
    # stopFlag.set()


class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        interval_seconds = 0
        if config.sync_inverval == 'hourly':
            interval_seconds = 3600
        elif config.sync_inverval == 'daily':
            interval_seconds = 3600 * 24
        elif config.sync_inverval == 'debug':
            interval_seconds = 10
        else:
            print("The configured interval is not supported. Use 'hourly' or 'daily' within your config.")
            exit(-749)
        while not self.stopped.wait(interval_seconds):
            sync_timer.sync()


start()
