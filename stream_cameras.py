import os
import vlc
import numpy as np
import cv2
import ctypes
import time
from screeninfo import get_monitors



class VLCPlayer:
    def __init__(self, url):
        # VLC instance with added network caching and no hardware acceleration
        self.instance = vlc.Instance(
            "--no-audio", "--no-xlib", "--video-title-show",
            "--no-video-title", "--avcodec-hw=none", "--network-caching=1000"
        )
        self.player = self.instance.media_player_new()
        self.width = 640  # Temporary placeholder
        self.height = 480  # Temporary placeholder
        self.frame_data = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        self.frame_pointer = self.frame_data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        self.setup_vlc()
        self.set_media(url)

    def setup_vlc(self):
        self.lock_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(self.lock_cb)
        self.unlock_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(self.unlock_cb)
        self.display_cb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)(self.display_cb)

        self.player.video_set_callbacks(self.lock_cb, self.unlock_cb, self.display_cb, None)
        self.player.video_set_format("RV32", self.width, self.height, self.width * 4)

    def set_media(self, url):
        self.media = self.instance.media_new(url)
        self.player.set_media(self.media)

    def lock_cb(self, opaque, planes):
        planes[0] = ctypes.cast(self.frame_pointer, ctypes.c_void_p)

    def unlock_cb(self, opaque, picture, planes):
        pass

    def display_cb(self, opaque, picture):
        pass

    def start(self):
        self.player.play()

    def stop(self):
        self.player.stop()

    def get_frame(self):
        return np.copy(self.frame_data)


if __name__ == "__main__":

    # Set the screen screen
    os.environ["DISPLAY"] = ':0'

    # Hide the mouse
    os.system("unclutter -idle 0 &")


    url_list = [
        "https://61e0c5d388c2e.streamlock.net/live/QAnne_N_Roy_NS.stream/chunklist_w80172027.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/2_Pike_NS.stream/chunklist_w144460210.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/5_Pike_NS.stream/chunklist_w1546202334.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/Broadway_E_Pike_EW.stream/chunklist_w525067259.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/23_Union_NS.stream/chunklist_w2126376810.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/Aurora_N_46_NS.stream/chunklist_w701844251.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/Stewart_Denny_EW.stream/chunklist_w477619834.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/3_N_Denny_EW.stream/chunklist_w1935047884.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/9_Pine_EW.stream/chunklist_w1290193883.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/5_Battery_East.stream/chunklist_w1120770203.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/3_Wall_NS.stream/chunklist_w454112638.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/1_Broad_NS.stream/chunklist_w505604715.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/8_Howell_EW.stream/chunklist_w1165616740.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/4_Virginia_EW.stream/chunklist_w23008384.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/6_Pine_EW.stream/chunklist_w1996305817.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/1_Seneca_EW.stream/chunklist_w901636604.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/1_Madison_NS.stream/chunklist_w1918683447.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/2_Marion_NS.stream/chunklist_w718268251.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/5_S_Washington_NS.stream/chunklist_w163265122.m3u8",
        "https://61e0c5d388c2e.streamlock.net/live/4_S_Jackson_NS.stream/chunklist_w789828686.m3u8"
    ]

    player = VLCPlayer(url_list[0])
    player.start()

    cv2.namedWindow("Video Stream", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video Stream", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Get screen dimensions using screeninfo
    monitor = get_monitors()[0]  # Assuming a single monitor setup
    screen_width = monitor.width
    screen_height = monitor.height

    start_time = time.time()
    url_index = 0

    while True:
        try:
            frame = player.get_frame()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

            # Resize the frame to fill the entire screen
            frame_rgb = cv2.resize(frame_rgb, (screen_width, screen_height))

            cv2.imshow("Video Stream", frame_rgb)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Switch video every 15 seconds
            if time.time() - start_time >= 15:
                player.stop()
                url_index = (url_index + 1) % len(url_list)  # Move to the next URL
                player.set_media(url_list[url_index])
                player.start()
                start_time = time.time()

        except Exception as e:
            print(f"Error occurred: {e}")
            # Restart the player if an error occurs
            player.stop()
            player.set_media(url_list[url_index])
            player.start()

    cv2.destroyAllWindows()
    player.stop()
