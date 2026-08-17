import configparser
from pathlib import Path
from optimizer.games.base import Game
from optimizer.core.backup import BackupManager
import shutil

class CS2Game(Game):
    def __init__(self, game_path: Path):
        super().__init__(game_path)
        self.cfg_path = game_path / "cfg"
        self.video_path = self.cfg_path / "video.txt"
        self.autoexec_path = self.cfg_path / "autoexec.cfg"
        self.backup_manager = BackupManager(game_path)

    def load(self):
        # Парсинг video.txt (CS2 использует похожий формат, но проще)
        self.config = {}
        if self.video_path.exists():
            with open(self.video_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        self.config[key.strip()] = value.strip()

    def save(self):
        self.backup_manager.create_backup(self.video_path)
        with open(self.video_path, 'w') as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")

    def set_setting(self, key: str, value):
        self.config[key] = value

    def apply_preset(self, preset: dict):
        for key, value in preset.items():
            self.set_setting(key, value)
        self.save()

    def restore_backup(self) -> bool:
        return self.backup_manager.restore_latest(self.video_path)

    @staticmethod
    def detect() -> Path | None:
        paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo"),
            Path("D:/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo"),
            Path("C:/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo"),
        ]
        for p in paths:
            if p.exists():
                return p
        return None

    @staticmethod
    def get_name() -> str:
        return "CS2"