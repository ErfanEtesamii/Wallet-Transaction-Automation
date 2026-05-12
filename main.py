import time
import logging
import random
import keyboard
from pathlib import Path
from config_loader import AppConfig
from wallet_selector import WalletSelector
from telegram_logger import TelegramLogger
from ui_automation import UIAutomation

class KeplrAutomationApp:
    def __init__(self):
        self.config = AppConfig("config.json")
        Path(self.config.get("screenshot_dir", "logs/screenshots")).mkdir(parents=True, exist_ok=True)
        Path(self.config.get("log_file", "logs/app.log")).parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=self.config.get("log_file", "logs/app.log"),
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s"
        )
        self.logger = logging.getLogger("txbot")
        self.telegram = TelegramLogger(
            self.config.telegram_token,
            self.config.telegram_chat_id,
            enabled=self.config.get("telegram_enabled", True),
            min_interval=self.config.get("telegram_min_interval_sec", 2)
        )
        self.wallets = WalletSelector(self.config.get("excel_path", "data/wallets.xlsx"))
        self.ui = UIAutomation(self.config.data, self.logger)
        self.stop_requested = False
        self.paused = False
        self.amount_cfg = self.config.get("amounts", {})
        self.urls = self.config.get("urls", {})
        self.targets = self.config.get("limits", {})
        self.interval_cfg = self.config.get("intervals", {})
        self.amount_choices = self.amount_cfg.get("choices", ["0.001", "0.0001", "0.00001", "0.000001"])
        self.amount_holesky = self.amount_cfg.get("holesky", "0.00001")
        self.amount_babylon = self.amount_cfg.get("babylon", "0.000001")
        self.amount_xion = self.amount_cfg.get("xion", "0.000001")
        self.amount_sei = self.amount_cfg.get("sei", "0.000001")
        self.counter_holesky = 0
        self.counter_babylon = 0
        self.counter_xion = 0
        self.counter_sei = 0
        self.interval_holesky = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
        self.interval_babylon = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
        self.interval_xion = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
        self.interval_sei = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
        self.fail_streak = 0
        self.current_wallet = None

    def log(self, msg):
        self.logger.info(msg)
        self.telegram.send(msg)
        print(msg)

    def save_wallet(self):
        if self.current_wallet:
            self.wallets.update_wallet(
                self.current_wallet["name"],
                self.current_wallet["HoleskyTransaction"],
                self.current_wallet["BabylonTransaction"],
                self.current_wallet["XionTransaction"],
                self.current_wallet["SeiTransaction"]
            )
            self.wallets.save()

    def should_stop(self):
        if keyboard.is_pressed("esc"):
            self.log("Detected ESC key press. Exiting...")
            self.stop_requested = True
        if keyboard.is_pressed("f8"):
            self.paused = not self.paused
            self.log("Paused." if self.paused else "Resumed.")
            time.sleep(0.5)
        return self.stop_requested

    def pause_loop(self):
        while self.paused and not self.stop_requested:
            time.sleep(0.3)
            self.should_stop()

    def update_amounts(self, name):
        if name == "holesky":
            self.counter_holesky += 1
            if self.counter_holesky >= self.interval_holesky:
                self.amount_holesky = random.choice(self.amount_choices)
                self.counter_holesky = 0
                self.interval_holesky = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
                self.log(f"🔁 [Holesky] Amount switched to: {self.amount_holesky}")
        elif name == "babylon":
            self.counter_babylon += 1
            if self.counter_babylon >= self.interval_babylon:
                self.amount_babylon = random.choice(self.amount_choices)
                self.counter_babylon = 0
                self.interval_babylon = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
                self.log(f"🔁 [Babylon] Amount switched to: {self.amount_babylon}")
        elif name == "xion":
            self.counter_xion += 1
            if self.counter_xion >= self.interval_xion:
                self.amount_xion = random.choice(self.amount_choices)
                self.counter_xion = 0
                self.interval_xion = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
                self.log(f"🔁 [Xion] Amount switched to: {self.amount_xion}")
        elif name == "sei":
            self.counter_sei += 1
            if self.counter_sei >= self.interval_sei:
                self.amount_sei = random.choice(self.amount_choices)
                self.counter_sei = 0
                self.interval_sei = random.randint(self.interval_cfg.get("min", 50), self.interval_cfg.get("max", 60))
                self.log(f"🔁 [Sei] Amount switched to: {self.amount_sei}")

    def transaction(self, wallet_tx, named_prepare_fn, is_sepolia=False):
        self.fail_streak = 0
        self.current_counter = 0
        name, prepare_fn = named_prepare_fn
        max_fail = self.targets.get("max_fail_streak", 10)

        while self.current_counter < wallet_tx and not self.stop_requested:
            self.pause_loop()
            if self.should_stop():
                break

            if self.fail_streak == 0:
                prepare_fn()
            else:
                self.ui.click(*self.config.data["coords"]["transfer_button"])
                time.sleep(1)

            start_time = time.time()
            transfer_ok = True
            while True:
                self.ui.click(*self.config.data["coords"]["approve_click"])
                time.sleep(0.1)
                if self.ui.pixel_matches(1181, 683, self.config.data["colors"]["final_button_color"]):
                    self.ui.click(1181, 683)
                    break
                if time.time() - start_time > 30:
                    transfer_ok = False
                    self.fail_streak += 1
                    self.log(f"❌ Failed TX #{self.fail_streak} (click transfer timeout)")
                    break

            if self.fail_streak >= max_fail:
                self.log("10 consecutive failed transactions. Exiting.")
                self.stop_requested = True
                break

            if transfer_ok:
                while True:
                    self.ui.click(*self.config.data["coords"]["approve_button"])
                    time.sleep(0.1)
                    color = self.config.data["colors"]["sepolia_approve_button_color"] if is_sepolia else self.config.data["colors"]["approve_button_color"]
                    pos = self.config.data["coords"]["sepolia_approve"] if is_sepolia else self.config.data["coords"]["normal_approve"]
                    self.ui.click(*pos)
                    time.sleep(1)
                    if self.ui.pixel_matches(pos[0], pos[1], color):
                        self.ui.click(*pos)
                        if is_sepolia:
                            time.sleep(1)
                            self.ui.click(*pos)
                        break
                    if time.time() - start_time > 40:
                        self.fail_streak += 1
                        self.log(f"❌ Failed TX #{self.fail_streak} (approve timeout)")
                        break

            if not transfer_ok or self.fail_streak >= max_fail:
                break

            start_time = time.time()
            while True:
                if self.ui.pixel_matches(1241, 674, self.config.data["colors"]["final_button_color"]):
                    self.current_counter += 1
                    self.fail_streak = 0
                    self.update_amounts(name)
                    if name == "holesky":
                        self.current_wallet["HoleskyTransaction"] += 1
                    elif name == "babylon":
                        self.current_wallet["BabylonTransaction"] += 1
                    elif name == "xion":
                        self.current_wallet["XionTransaction"] += 1
                    elif name == "sei":
                        self.current_wallet["SeiTransaction"] += 1
                    self.log(f"✅ Success TX in {name.capitalize()} #{self.current_counter}")
                    break
                if time.time() - start_time > 75:
                    self.fail_streak += 1
                    self.log(f"❌ Failed TX #{self.fail_streak} (final confirmation timeout)")
                    break

    def one_chain_holesky(self, holesky_tx):
        holesky_needed = max(0, self.targets.get("holesky_target", 500) - int(holesky_tx))
        self.log("Starting Holesky transaction")
        self.log(f"Holesky: {holesky_needed} tx remaining for wallet '{self.current_wallet['name']}'")
        time.sleep(2)
        self.ui.click(*self.config.data["coords"]["chain_home"])
        self.transaction(holesky_needed, ("holesky", lambda: self.ui.prepare_transaction(self.amount_holesky, self.urls["xion_hol"])), is_sepolia=True)

    def one_chain_babylon(self, babylon_tx):
        babylon_needed = max(0, self.targets.get("babylon_target", 500) - int(babylon_tx))
        self.log("Starting Babylon transaction")
        self.log(f"Babylon: {babylon_needed} tx remaining for wallet '{self.current_wallet['name']}'")
        time.sleep(2)
        self.ui.click(*self.config.data["coords"]["chain_home"])
        self.transaction(babylon_needed, ("babylon", lambda: self.ui.prepare_transaction(self.amount_babylon, self.urls["xion_bab"])), is_sepolia=False)

    def one_chain_xion(self, xion_tx):
        xion_needed = max(0, self.targets.get("xion_target", 500) - int(xion_tx))
        self.log("Starting Xion transaction")
        self.log(f"Xion: {xion_needed} tx remaining for wallet '{self.current_wallet['name']}'")
        time.sleep(2)
        self.ui.click(*self.config.data["coords"]["chain_home"])
        self.transaction(xion_needed, ("xion", lambda: self.ui.prepare_transaction(self.amount_sei, self.urls["sei_xion"])), is_sepolia=True)

    def one_chain_sei(self, sei_tx):
        sei_needed = max(0, self.targets.get("sei_target", 200) - int(sei_tx))
        self.log("Starting Sei transaction")
        self.log(f"Sei: {sei_needed} tx remaining for wallet '{self.current_wallet['name']}'")
        time.sleep(2)
        self.ui.click(*self.config.data["coords"]["chain_home"])
        self.transaction(sei_needed, ("sei", lambda: self.ui.prepare_transaction(self.amount_sei, self.urls["xion_sei"])), is_sepolia=False)

    def run_one_wallet(self):
        holesky_needed = max(0, self.targets.get("holesky_target", 500) - self.current_wallet["HoleskyTransaction"])
        babylon_needed = max(0, self.targets.get("babylon_target", 500) - self.current_wallet["BabylonTransaction"])
        xion_needed = max(0, self.targets.get("xion_target", 500) - self.current_wallet["XionTransaction"])
        sei_needed = max(0, self.targets.get("sei_target", 200) - self.current_wallet["SeiTransaction"])

        choices = [
            ("Holesky", self.one_chain_holesky, self.current_wallet["HoleskyTransaction"], holesky_needed),
            ("Babylon", self.one_chain_babylon, self.current_wallet["BabylonTransaction"], babylon_needed),
            ("Xion", self.one_chain_xion, self.current_wallet["XionTransaction"], xion_needed),
            ("Sei", self.one_chain_sei, self.current_wallet["SeiTransaction"], sei_needed)
        ]
        random.shuffle(choices)
        for name, func, tx_count, needed in choices:
            if self.stop_requested:
                break
            if needed > 0:
                self.log(f"{name}: {needed} tx remaining for wallet '{self.current_wallet['name']}'")
                func(tx_count)

        if holesky_needed <= 0 and babylon_needed <= 0 and xion_needed <= 0 and sei_needed <= 0:
            self.log(f"Wallet {self.current_wallet['name']} already completed all transactions.")
            self.stop_requested = True

    def main_loop(self, mode, requested_wallet_count):
        processed = 0
        while processed < requested_wallet_count and not self.stop_requested:
            self.pause_loop()
            if self.should_stop():
                break

            wallet_info = self.wallets.get_random_incomplete_wallet()
            if wallet_info is None:
                self.log("No more incomplete wallets found.")
                break

            self.current_wallet = wallet_info
            try:
                self.log(str(wallet_info))
                self.ui.switch_wallet_keplr(wallet_info["name"])
                self.ui.switch_wallet_rabby(wallet_info["name"])
                time.sleep(1)

                if mode == "xion":
                    self.one_chain_xion(wallet_info["XionTransaction"])
                elif mode == "babylon":
                    self.one_chain_babylon(wallet_info["BabylonTransaction"])
                elif mode == "holesky":
                    self.one_chain_holesky(wallet_info["HoleskyTransaction"])
                elif mode == "sei":
                    self.one_chain_sei(wallet_info["SeiTransaction"])
                elif mode == "full":
                    self.run_one_wallet()
            finally:
                self.save_wallet()

            if not self.stop_requested:
                if (
                    self.current_wallet["HoleskyTransaction"] >= self.targets.get("holesky_target", 500)
                    and self.current_wallet["BabylonTransaction"] >= self.targets.get("babylon_target", 500)
                    and self.current_wallet["XionTransaction"] >= self.targets.get("xion_target", 500)
                    and self.current_wallet["SeiTransaction"] >= self.targets.get("sei_target", 200)
                ):
                    self.wallets.mark_wallet_done(self.current_wallet["name"])
                    self.wallets.save()
                    self.log(f"Marked {self.current_wallet['name']} as complete.")
                processed += 1

    def run(self):
        requested_wallet_count = int(input("How many wallets to process? ").strip())

        print("Select an option to run:")
        print("0: Run one_chain_xion")
        print("1: Run one_chain_babylon")
        print("2: Run one_chain_holesky")
        print("3: Run one_chain_sei")
        print("4: Run one_wallet")
        choice = input("Enter your option: ").strip()

        try:
            if choice == "0":
                self.main_loop("xion", requested_wallet_count)
            elif choice == "1":
                self.main_loop("babylon", requested_wallet_count)
            elif choice == "2":
                self.main_loop("holesky", requested_wallet_count)
            elif choice == "3":
                self.main_loop("sei", requested_wallet_count)
            elif choice == "4":
                self.main_loop("full", requested_wallet_count)
            else:
                print("Invalid choice.")
        except KeyboardInterrupt:
            self.log("Program interrupted by user (Ctrl+C). Saving current progress...")
        finally:
            self.save_wallet()
            self.log("Done")
            self.shutdown_with_delay()

    def shutdown_with_delay(self):
        import threading
        import winsound
        import os
        print("⚠️ Typing No to stop shutdowning procces")
        winsound.Beep(1000, 500)
        user_input = []

        def get_input():
            answer = input("⏳ Please typing No..: ").strip()
            user_input.append(answer)

        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        input_thread.join(timeout=20)

        if user_input and user_input[0].lower() == "no":
            print("❎ ShutingDown proccess is Stoped")
        else:
            print("💤 ShutingDown, GoodBye.. ")
            os.system("taskkill /f /im chrome.exe")
            time.sleep(2)
            os.system("shutdown /s /t 0")

if __name__ == "__main__":
    KeplrAutomationApp().run()