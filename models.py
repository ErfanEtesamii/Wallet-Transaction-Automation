from dataclasses import dataclass

@dataclass
class WalletRecord:
    name: str
    holesky: int = 0
    babylon: int = 0
    xion: int = 0
    sei: int = 0
    done: int = 0