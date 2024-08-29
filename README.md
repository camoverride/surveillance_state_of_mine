# Surveillance State of Mind


## Setup

- `sudo apt-get install unclutter`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`


## Test

`python stream_cameras.py`


## Run in Production

Start a service with *systemd*. This will start the program when the computer starts and revive it when it dies:

- `mkdir -p ~/.config/systemd/user`

- Paste the contents of `display.service` into `~/.config/systemd/user/display.service`

Start the service using the commands below:

- `systemctl --user daemon-reload`
- `systemctl --user enable display.service`
- `systemctl --user start display.service`

Start it on boot: `sudo loginctl enable-linger pi`

Get the logs: `journalctl --user -u display.service`


## TODO

- make sure it runs without freezing / restarts
- add static when frames change
- add config to determine frame time
- add stream list to file
