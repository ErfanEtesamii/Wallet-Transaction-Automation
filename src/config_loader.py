import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    """Loads config.json (non-secret settings) and reads secrets from the
    environment (populated from .env by python-dotenv)."""

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

    def require_coords(self, *keys):
        """Fail fast at startup instead of crashing mid-run if a coordinate
        the automation depends on is missing from config.json."""
        coords = self.data.get("coords", {})
        missing = [k for k in keys if k not in coords]
        if missing:
            raise KeyError(f"config.json is missing required coords: {missing}")
