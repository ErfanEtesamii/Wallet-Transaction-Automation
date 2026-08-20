"""Entry point. All application logic lives in src/app.py."""
import platform

from src.app import TxAutomationApp

if __name__ == "__main__":
    if platform.system() != "Windows":
        print(
            "This tool relies on Windows-only pieces (winsound, taskkill, "
            "shutdown) for its optional end-of-run prompt, and its "
            "coordinates/hotkeys were tuned on Windows. It may still run "
            "elsewhere, but hasn't been tested there."
        )
    TxAutomationApp().run()
