import time
import requests

class TelegramLogger:
    def __init__(self, token, chat_id, enabled=True, min_interval=2):
        self.token = token
        self.chat_id = chat_id
        self.enabled = enabled and bool(token) and bool(chat_id)
        self.min_interval = min_interval
        self._last_sent = 0.0

    def send(self, message: str):
        if not self.enabled:
            return
        now = time.time()
        if now - self._last_sent < self.min_interval:
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": self.chat_id, "text": message}, timeout=10)
            self._last_sent = now
        except Exception:
            pass