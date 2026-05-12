import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class AppConfig:
    def __init__(self, path="config.json"):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Config not found: {self.path}")
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    @property
    def telegram_token(self):
        return os.getenv("TELEGRAM_TOKEN", "")

    @property
    def telegram_chat_id(self):
        return os.getenv("TELEGRAM_CHAT_ID", "")

    def get(self, key, default=None):
        return self.data.get(key, default)