# Surveillance State of Mind


## Setup

- `sudo apt-get install unclutter`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`


## Test

`python stream_cameras.py`


## Run in Production

Start a service and a timer with *systemd*. This will start the program when the computer starts and revive it when it dies:

- `mkdir -p ~/.config/systemd/user`

Add a timer to restart systemd every 1 hour. Copy the contents of `display.timer` to `~/.config/systemd/user/display.timer`, then:

- `systemctl --user daemon-reload`
- `systemctl --user enable display.timer`
- `systemctl --user start display.timer`

Then copy the contents of `display.service` into `~/.config/systemd/user/display.service`

- `systemctl --user daemon-reload`
- `systemctl --user enable display.service`
- `systemctl --user start display.service`

Start it on boot: `sudo loginctl enable-linger pi`

Get the logs: `journalctl --user -u display.service`


## TODO

- [ ] make sure it runs without freezing / restarts
    - added `display.timer` to restart every hour (on the hour) -- DISABLED THIS
    - tried adding hash function to check for changes, but it might be slow
        - hash every frame vs hash a frame every 15 secs!


- [ ] add static when frames change
- [ ] add config to determine frame time
- [X] add stream list to file
