import os
import vlc
import numpy as np
import cv2
import ctypes
import time
from screeninfo import get_monitors

from camera_info import url_list


class VLCPlayer:
    def __init__(self, url):
        self.instance = vlc.Instance(
            "--no-audio", "--no-xlib", "--video-title-show",
            "--no-video-title", "--avcodec-hw=none",
            "--network-caching=5000", "--clock-synchro=0", "--file-caching=5000",
            "--ts-seek-percent", "--sout-ts-shaping=1"
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


def main():


    player = None

    while True:
        try:
            player = VLCPlayer(url_list[0])
            player.start()

            cv2.namedWindow("Video Stream", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Video Stream", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            monitor = get_monitors()[0]
            screen_width = monitor.width
            screen_height = monitor.height

            start_time = time.time()
            url_index = 0

            while True:
                try:
                    frame = player.get_frame()
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

                    frame_rgb = cv2.resize(frame_rgb, (screen_width, screen_height))

                    cv2.imshow("Video Stream", frame_rgb)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    if time.time() - start_time >= 15:
                        player.stop()
                        url_index = (url_index + 1) % len(url_list)
                        player.set_media(url_list[url_index])
                        time.sleep(2)  # Small delay to allow the stream to stabilize
                        player.start()
                        start_time = time.time()

                except Exception as e:
                    print(f"Inner loop error occurred: {e}")
                    break  # Break the inner loop and restart

        except Exception as e:
            print(f"Outer loop error occurred: {e}")
            if player:
                player.stop()
            time.sleep(10)  # Increase the delay before retrying to allow recovery

        finally:
            cv2.destroyAllWindows()
            if player:
                player.stop()


if __name__ == "__main__":
    os.environ["DISPLAY"] = ':0'
    os.system("unclutter -idle 0 &")
    main()
