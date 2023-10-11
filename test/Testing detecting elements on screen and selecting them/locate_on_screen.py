"""
Technology from https://automatetheboringstuff.com/chapter18/#:~:text=You%20can%20also%20perform%20a,around%20these%20two%20function%20calls
and a stack exchange forum entry (no url recorded): Class WindowMgr()

Evolving demo to control pyPoB for testing purposes.
"""

# https://automatetheboringstuff.com/chapter18/#:~:text=You%20can%20also%20perform%20a,around%20these%20two%20function%20calls
import pyautogui
import re
import time

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-propenumprocexa
# ignore this error in pyCharm
import win32gui


def click_image(image: str):
    """

    :param image: str: full path to file
    :return:
    """
    size = pyautogui.locateOnScreen(image, 5)
    if size is not None:
        pyautogui.click(size.left + size.width / 2, size.top + size.height / 2)
        # Do not set this too long. A tooltip might hide the next button
        time.sleep(0.5)
    return size is not None


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__(self):
        """Constructor"""
        self._handle = None

    @property
    def handle(self):
        return self._handle

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd)), flags=re.IGNORECASE) is not None:
            print("find_window: Window Title:", str(win32gui.GetWindowText(hwnd)))
            print(f"find_window: Window Handle: {hwnd}")
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def _child_window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        print("_child_window_enum_callback", str(win32gui.GetWindowText(hwnd)))
        self.enum_child_windows(hwnd)

    def enum_child_windows(self, hwnd=0):
        _hwnd = hwnd == 0 and self.handle or hwnd
        win32gui.EnumChildWindows(_hwnd, self._child_window_enum_callback, None)

    def _properties_enum_callback(self, hwnd, prop_title, prop_data, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        print("_properties_enum_callback", prop_title, prop_data)

    def enum_properties(self, hwnd=0):
        print("enum_properties: Window Title:", str(win32gui.GetWindowText(self._handle)))
        print(f"enum_properties: Window Handle: {w.handle}")
        _hwnd = hwnd == 0 and self.handle or hwnd
        win32gui.EnumPropsEx(_hwnd, self._properties_enum_callback, None)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)


w = WindowMgr()
w.find_window_wildcard(".*chrome.*")
w.enum_properties()
# w.set_foreground()

# time.sleep(3)
#
# if click_image("G:/newTab.png"):
#     # click_image("G:/music.png")
#     click_image("G:/weather.png")
