#!/usr/bin/python3

import os
import time

from watchdog.observers import Observer
from watchdog.events import DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, \
    FileSystemEventHandler

import log


class ChangeHandler(FileSystemEventHandler):

    def __init__(self):
        self.reset()

    def on_any_event(self, event):
        if type(event) in [DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent]:
            self._changed = True
            self._time_of_change = time.time()

    def reset(self):
        self._changed = False
        self._time_of_change = 0

    @property
    def changed(self):
        return self._changed

    @property
    def time_of_change(self):
        return self._time_of_change


class PiFrameConfig:

    _ENV_VAR_USB_MOUNT_POINT = "PI_FRAME_USB_MOUNT_POINT"
    _ENV_VAR_USB_STORAGE_FILE = "PI_FRAME_USB_STORAGE_FILE"

    _ENV_VAR_CHANGE_TIMEOUT_SECS = "PI_FRAME_CHANGE_TIMEOUT_SECS"
    _ENV_VAR_EXECUTION_PAUSE_SECS = "PI_FRAME_EXECUTION_PAUSE_SECS"
    _ENV_VAR_DETECT_CHANGE_PAUSE_SECS = "PI_FRAME_DETECT_CHANGE_PAUSE_SECS"

    def __init__(self):
        self._usb_mount_point = os.getenv(self._ENV_VAR_USB_MOUNT_POINT)
        self._value_present(self._usb_mount_point, self._ENV_VAR_USB_MOUNT_POINT)

        self._usb_storage_file = os.getenv(self._ENV_VAR_USB_STORAGE_FILE)
        self._value_present(self._usb_storage_file, self._ENV_VAR_USB_STORAGE_FILE)

        self._change_timeout = os.getenv(self._ENV_VAR_CHANGE_TIMEOUT_SECS, 30)
        self._execution_pause = os.getenv(self._ENV_VAR_EXECUTION_PAUSE_SECS, 1)
        self._detect_change_pause = os.getenv(self._ENV_VAR_DETECT_CHANGE_PAUSE_SECS, 30)

        log.info(f"usb_mount_point = '{self.usb_mount_point}'; usb_storage_file = '{self.usb_storage_file}'; "
                 f"change_timeout = '{self.change_timeout}'; execution_pause = '{self.execution_pause}'; "
                 f"detect_change_pause = '{self.detect_change_pause}'")

    def _value_present(self, env_var_value: str, env_var_name: str) -> None:
        if not env_var_value or not env_var_value.strip():
            log.error(f"Missing config for {env_var_name}. Please check pi_frame.conf")
            raise ValueError

    @property
    def usb_mount_point(self) -> str:
        return self._usb_mount_point

    @property
    def usb_storage_file(self) -> str:
        return self._usb_storage_file

    @property
    def change_timeout(self) -> int:
        return self._change_timeout

    @property
    def execution_pause(self) -> int:
        return self._execution_pause

    @property
    def detect_change_pause(self) -> int:
        return self._detect_change_pause


def run():
    config = PiFrameConfig()
    command_sync_file_changes = "sync"
    command_disable_usb_storage = "modprobe -r g_mass_storage"
    command_enable_usb_storage = f"modprobe g_mass_storage file={config.usb_storage_file} stall=0 ro=1"

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

                if time_out >= config.change_timeout:
                    log.info(f"File change detected at {event_handler.time_of_change} - triggering USB refresh...")
                    os.system(command_disable_usb_storage)
                    time.sleep(config.execution_pause)
                    os.system(command_sync_file_changes)
                    time.sleep(config.execution_pause)
                    os.system(command_enable_usb_storage)
                    event_handler.reset()
                    log.info(f"USB refresh complete.")

                time.sleep(config.execution_pause)

            time.sleep(config.detect_change_pause)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    run()
