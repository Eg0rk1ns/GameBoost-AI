import vdf
from pathlib import Path
from optimizer.games.base import Game
from optimizer.core.backup import BackupManager

class Dota2Game(Game):
    def __init__(self, game_path: Path):
        super().__init__(game_path)
        self.video_path = game_path / "cfg/video.txt"
        self.backup_manager = BackupManager(game_path)

    def load(self):
        if self.video_path.exists():
            with open(self.video_path, 'r', encoding='utf-8') as f:
                self.config = vdf.loads(f.read())
        else:
            raise FileNotFoundError(f"video.txt not found at {self.video_path}")

    def save(self):
        self.backup_manager.create_backup(self.video_path)
        with open(self.video_path, 'w', encoding='utf-8') as f:
            vdf.dump(self.config, f, pretty=True)

    def set_setting(self, key: str, value):
        if "Video" not in self.config:
            self.config["Video"] = {}
        self.config["Video"][key] = value

    def apply_preset(self, preset: dict):
        for key, value in preset.items():
            self.set_setting(key, value)
        self.save()

    def restore_backup(self) -> bool:
        return self.backup_manager.restore_latest(self.video_path)

    @staticmethod
    def detect() -> Path | None:
        from optimizer.utils.paths import find_dota2_path
        return find_dota2_path()

    @staticmethod
    def get_name() -> str:
        return "Dota 2"