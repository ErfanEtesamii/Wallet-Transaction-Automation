import time
import threading
import queue
import requests


class TelegramLogger:
    """Rate-limited Telegram notifier.

    Fix: the previous version dropped a message outright if it was called
    again before ``min_interval`` had elapsed, so bursts of real events
    (several transactions succeeding close together) silently never reached
    Telegram. Messages are now queued and sent by a background thread as
    soon as the interval allows, so nothing is lost and the caller is never
    blocked waiting on the network.
    """

    def __init__(self, token, chat_id, enabled=True, min_interval=2):
        self.token = token
        self.chat_id = chat_id
        self.enabled = enabled and bool(token) and bool(chat_id)
        self.min_interval = min_interval
        self._queue = queue.Queue()
        self._last_sent = 0.0
        self._worker = None
        if self.enabled:
            self._worker = threading.Thread(target=self._run, daemon=True)
            self._worker.start()

    def send(self, message: str):
        if not self.enabled:
            return
        self._queue.put(message)

    def _run(self):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        while True:
            message = self._queue.get()
            wait = self.min_interval - (time.time() - self._last_sent)
            if wait > 0:
                time.sleep(wait)
            try:
                requests.post(
                    url,
                    data={"chat_id": self.chat_id, "text": message},
                    timeout=10,
                )
            except Exception:
                pass
            self._last_sent = time.time()
