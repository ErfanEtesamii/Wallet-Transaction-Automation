import time
import pyautogui
import pyperclip
from src.utils import retry, wait_until


class UIAutomation:
    def __init__(self, config, logger, stop_fn=None):
        self.config = config
        self.logger = logger
        # Lets the caller (the main app) tell long internal waits to give up
        # early when the user hits ESC, instead of them running to full
        # timeout regardless.
        self.stop_fn = stop_fn or (lambda: False)
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
        return wait_until(
            lambda: self.pixel_matches(x, y, color),
            timeout=timeout,
            interval=interval,
            stop_fn=self.stop_fn,
        )

    def screenshot_failure(self, path):
        pyautogui.screenshot(path)

    def switch_wallet_keplr(self, wallet_name):
        c = self.config["coords"]
        self.click(*c["keplr_icon"])
        time.sleep(4)
        self.click(*c["keplr_search"])
        time.sleep(2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")
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
        pyautogui.press("delete")
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

    def prepare_transaction(self, amount, url, timeout=30):
        """Fill in the transfer form (address bar -> URL -> amount).

        Fix: this used to end with an unbounded ``while True`` loop waiting
        for the page's final button to render. If that button never
        appeared (page failed to load, wrong window focus, a captcha, a UI
        change) the whole script hung forever with no log line and no way
        to recover short of killing the process. It now waits up to
        ``timeout`` seconds and returns False so the caller can log it,
        count it as a failed attempt, and retry - the same way every other
        wait in this codebase already behaves.
        """
        c = self.config["coords"]
        self.click(*c["browser_address_bar"])
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")
        self.paste_text(url)
        pyautogui.press("enter")
        time.sleep(2)
        self.verify_human()
        time.sleep(2)

        if not self.wait_for_pixel(1231, 693, self.config["colors"]["final_button_color"], timeout=timeout):
            self.logger.warning("prepare_transaction: final button never appeared, aborting this attempt")
            return False
        pyautogui.click(1231, 693)

        time.sleep(2)
        pyautogui.click(*c["amount_field_click_2"])
        time.sleep(2)
        pyautogui.click(*c["amount_field_click"])
        time.sleep(4)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")
        self.type_text(amount)
        return True
