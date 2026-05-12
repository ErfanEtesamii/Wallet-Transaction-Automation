import time
from pathlib import Path
import pyautogui
import pyperclip
from utils import retry

class UIAutomation:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.12

    @retry(max_attempts=3, base_delay=0.4)
    def click(self, x, y):
        pyautogui.click(x, y)

    def type_text(self, text):
        pyautogui.write(str(text), interval=0.02)

    def paste_text(self, text):
        pyperclip.copy(str(text))
        pyautogui.hotkey("ctrl", "v")

    def pixel_matches(self, x, y, color):
        return pyautogui.screenshot().getpixel((x, y)) == tuple(color)

    def wait_for_pixel(self, x, y, color, timeout=30, interval=0.2):
        start = time.time()
        while time.time() - start < timeout:
            if self.pixel_matches(x, y, color):
                return True
            time.sleep(interval)
        return False

    def screenshot_failure(self, path):
        pyautogui.screenshot(path)

    def switch_wallet_keplr(self, wallet_name):
        c = self.config["coords"]
        self.click(*c["keplr_icon"])
        time.sleep(4)
        self.click(*c["keplr_search"])
        time.sleep(2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("delete")
        self.type_text(wallet_name.lower())
        time.sleep(3)
        self.click(*c["keplr_submit"])

    def switch_wallet_rabby(self, wallet_name):
        c = self.config["coords"]
        self.click(*c["rabby_icon"])
        time.sleep(4)
        self.click(*c["rabby_search"])
        time.sleep(2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("delete")
        time.sleep(2)
        self.type_text(wallet_name.lower())
        time.sleep(3)
        self.click(*c["rabby_submit"])

    def verify_human(self):
        c = self.config["coords"]
        dark = self.config["colors"]["human_check_dark_color"]
        pyautogui.moveTo(*c["human_check"])
        time.sleep(2)
        if pyautogui.screenshot().getpixel(tuple(c["human_check"])) == tuple(dark):
            time.sleep(10)
            pyautogui.click(*c["human_check_confirm"])

    def prepare_transaction(self, amount, url):
        c = self.config["coords"]
        self.click(*c["browser_address_bar"])
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("delete")
        self.paste_text(url)
        pyautogui.press("enter")
        time.sleep(2)
        self.verify_human()
        time.sleep(2)
        while True:
            pyautogui.moveTo(1231, 693)
            time.sleep(0.1)
            if pyautogui.screenshot().getpixel((1231, 693)) == tuple(self.config["colors"]["final_button_color"]):
                pyautogui.click(1231, 693)
                break
        time.sleep(2)
        pyautogui.click(1069, 572)
        time.sleep(2)
        pyautogui.click(1084, 583)
        time.sleep(4)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("delete")
        self.type_text(amount)

    def wait_and_click_approve(self, is_sepolia=False, timeout=40):
        c = self.config["coords"]
        color = self.config["colors"]["sepolia_approve_button_color"] if is_sepolia else self.config["colors"]["approve_button_color"]
        pos = c["sepolia_approve"] if is_sepolia else c["normal_approve"]
        start = time.time()
        while True:
            pyautogui.moveTo(*pos)
            time.sleep(1)
            if pyautogui.screenshot().getpixel(pyautogui.position()) == tuple(color):
                pyautogui.click(pyautogui.position())
                if is_sepolia:
                    time.sleep(1)
                    pyautogui.click(pyautogui.position())
                return True
            if time.time() - start > timeout:
                return False