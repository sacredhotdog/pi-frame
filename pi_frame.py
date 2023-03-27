#!/usr/bin/python3

import os
import time

from watchdog.observers import Observer
from watchdog.events import DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, \
    FileSystemEventHandler

import log
from pi_frame_config import PiFrameConfig


class ChangeHandler(FileSystemEventHandler):

    def __init__(self):
        self.reset()
        self._valid_events = [DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent]

    def on_any_event(self, event):
        log.debug(f"ChangeHandler: change detected [{event}]")

        if type(event) in self._valid_events:
            self._changed = True
            self._time_of_change = time.time()
        else:
            log.debug(f"Ineligible change, ignoring. Not one of {self._valid_events}")

    def reset(self):
        log.debug("ChangeHandler.reset() called")
        self._changed = False
        self._time_of_change = 0

    @property
    def changed(self):
        return self._changed

    @property
    def time_of_change(self):
        return self._time_of_change


def run():
    config = PiFrameConfig()
    command_sync_file_changes = "sync"
    command_disable_usb_storage = "sudo modprobe -r g_mass_storage"
    command_enable_usb_storage = f"sudo modprobe g_mass_storage file={config.usb_storage_file} stall=0 ro=1"

    log.info("Activating USB storage...")
    os.system(command_sync_file_changes)
    time.sleep(config.execution_pause)
    os.system(command_enable_usb_storage)
    log.info("Activation complete.")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=config.usb_mount_point, recursive=True)
    observer.start()
    log.info("Now watching for file changes...")

    try:
        while True:
            while event_handler.changed:
                time_out = time.time() - event_handler.time_of_change
                log.debug(f"Time elapsed = {time_out}s; timeout limit = {config.change_timeout}s")

                if time_out >= config.change_timeout:
                    log.info(f"File change detected, triggering USB refresh")
                    os.system(command_disable_usb_storage)
                    time.sleep(config.execution_pause)
                    os.system(command_sync_file_changes)
                    time.sleep(config.execution_pause)
                    os.system(command_enable_usb_storage)
                    event_handler.reset()
                    log.info(f"USB refresh complete")

                log.debug(f"Pausing execution for {config.execution_pause}s")
                time.sleep(config.execution_pause)

            log.debug(f"Pausing change detection for {config.detect_change_pause}s")
            time.sleep(config.detect_change_pause)
    except Exception as error:
        log.error(error)
        log.warn("Change detection interrupted - stopping")
        observer.stop()

    observer.join()
    log.warn("Stopped")


if __name__ == "__main__":
    run()
