#!/bin/bash


# root or bust
if [[ "$EUID" -ne 0 ]]
then
    echo "Please run as root."
    exit
fi


CURRENT_USER="$(logname)"

su -c "sudo apt-get install virtualenv -y" ${CURRENT_USER}
su -c "virtualenv -p python3 venv" ${CURRENT_USER}
su -c "source venv/bin/activate && pip install -r requirements.txt" ${CURRENT_USER}

source ./pi_frame.conf
CURRENT_WORKING_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


## 'Installation' location

if [[ -e "$PI_FRAME_INSTALLATION_DIRECTORY" && -h "$PI_FRAME_INSTALLATION_DIRECTORY" ]]
then
  unlink ${PI_FRAME_INSTALLATION_DIRECTORY}
fi

ln -s ${CURRENT_WORKING_DIRECTORY} ${PI_FRAME_INSTALLATION_DIRECTORY}

# Ensure that permissions are correct
chown -h ${CURRENT_USER}:${CURRENT_USER} ${PI_FRAME_INSTALLATION_DIRECTORY}


## Logging

# Ensure log directory exists and that permissions are correct
mkdir -p ${PI_FRAME_LOGGING_DIRECTORY}
chown ${CURRENT_USER}:${CURRENT_USER} ${PI_FRAME_LOGGING_DIRECTORY}

# logrotate configuration
cat > /etc/logrotate.d/pi-frame <<LOGGING_POLICY
${PI_FRAME_LOGGING_DIRECTORY}/pi-frame.log {
  rotate 4
  weekly
  compress
  missingok
  notifempty
  create 660 ${CURRENT_USER} ${CURRENT_USER}
}
LOGGING_POLICY


## pi-frame service

PI_FRAME_SERVICE_NAME="pi-frame.service"
PI_FRAME_SERVICE_PATH="/etc/systemd/system/${PI_FRAME_SERVICE_NAME}"
PI_FRAME_SERVICE_ENTRY_POINT="pi_frame.py"

# Make sure that any previous installations are not running
systemctl stop ${PI_FRAME_SERVICE_NAME}

# systemctl service definition
cat > ${PI_FRAME_SERVICE_PATH} <<SERVICE_DEFINITION
[Unit]
Description=${PI_FRAME_SERVICE_NAME}
After=multi-user.target
StartLimitIntervalSec=120
StartLimitBurst=6

[Service]
Type=simple
User=${CURRENT_USER}
Group=${CURRENT_USER}
Environment="PI_FRAME_LOG_FILE=${PI_FRAME_LOGGING_DIRECTORY}/pi-frame.log"
Environment="PI_FRAME_USB_MOUNT_POINT=${PI_FRAME_USB_MOUNT_POINT}"
Environment="PI_FRAME_USB_STORAGE_FILE=${PI_FRAME_USB_STORAGE_FILE}"
Environment="PI_FRAME_CHANGE_TIMEOUT_SECS=${PI_FRAME_CHANGE_TIMEOUT_SECS}"
Environment="PI_FRAME_COMMAND_SLEEP_SECS=${PI_FRAME_COMMAND_SLEEP_SECS}"
Environment="PI_FRAME_CHANGE_PAUSE_SECS=${PI_FRAME_CHANGE_PAUSE_SECS}"
ExecStart=${PI_FRAME_INSTALLATION_DIRECTORY}/venv/bin/python ${PI_FRAME_INSTALLATION_DIRECTORY}/${PI_FRAME_SERVICE_ENTRY_POINT}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_DEFINITION


# Fire everything up
chmod 644 ${PI_FRAME_SERVICE_PATH}
systemctl daemon-reload
systemctl enable ${PI_FRAME_SERVICE_NAME}
systemctl start ${PI_FRAME_SERVICE_NAME}
