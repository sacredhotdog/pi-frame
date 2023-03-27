import os

import log


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

        self._change_timeout = int(os.getenv(self._ENV_VAR_CHANGE_TIMEOUT_SECS, 30))
        self._execution_pause = int(os.getenv(self._ENV_VAR_EXECUTION_PAUSE_SECS, 1))
        self._detect_change_pause = int(os.getenv(self._ENV_VAR_DETECT_CHANGE_PAUSE_SECS, 30))

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
