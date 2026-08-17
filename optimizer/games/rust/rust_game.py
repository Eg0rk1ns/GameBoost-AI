from pathlib import Path
from optimizer.games.base import Game
from optimizer.core.backup import BackupManager
import configparser
import os

class RustGame(Game):
    def __init__(self, game_path: Path):
        super().__init__(game_path)
        # Путь к клиентскому конфигу Rust
        self.cfg_path = game_path / "cfg"
        self.client_cfg = self.cfg_path / "client.cfg"
        self.backup_manager = BackupManager(game_path)
        self.config = None

    def load(self):
        """Загружает конфиг client.cfg"""
        self.config = {}
        if self.client_cfg.exists():
            with open(self.client_cfg, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('//'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()

    def save(self):
        """Сохраняет конфиг, создавая бекап"""
        self.backup_manager.create_backup(self.client_cfg)
        with open(self.client_cfg, 'w', encoding='utf-8') as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")

    def set_setting(self, key: str, value):
        self.config[key] = value

    def apply_preset(self, preset: dict):
        for key, value in preset.items():
            self.set_setting(key, value)
        self.save()

    def restore_backup(self) -> bool:
        return self.backup_manager.restore_latest(self.client_cfg)

    @staticmethod
    def detect() -> Path | None:
        """Поиск пути к Rust через стандартные папки Steam"""
        steam_paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Rust"),
            Path("D:/Steam/steamapps/common/Rust"),
            Path("C:/Steam/steamapps/common/Rust"),
            Path("E:/Steam/steamapps/common/Rust"),
        ]
        for p in steam_paths:
            if p.exists():
                return p / "cfg"
        return None

    @staticmethod
    def get_name() -> str:
        return "Rust"