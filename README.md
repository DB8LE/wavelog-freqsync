# Wavelog Frequency Sync

Automatically synchronize the frequency from a rigctld instance to wavelog.

## Requirements

The only requirement is python3-requests

## Installing

First, copy config.example.toml to config.toml and edit the values in the file.

Then make sure you have rigctld running and run `python3 main.py`

### SystemD service

To install the systemd service, follow these steps:

1. Make sure you have rigctld running in another service
2. Run `sudo cp wavelog-freqsync.service /etc/systemd/system/`
3. Edit the file `/etc/systemd/system/wavelog-freqsync.service` with your favourite editor and fill in all required values
4. Run `sudo systemctl daemon-reload`, and then enable the service with `sudo systemctl enable wavelog-freqsync.service`
