import vdf
from pathlib import Path
from optimizer.core.backup import BackupManager

class Dota2Config:
    def __init__(self, dota_path: Path):
        self.video_path = dota_path / "cfg/video.txt"
        self.data = None
        self.backup_manager = BackupManager(dota_path)

    def load(self):
        if self.video_path.exists():
            with open(self.video_path, 'r', encoding='utf-8') as f:
                self.data = vdf.loads(f.read())
        else:
            raise FileNotFoundError(f"video.txt not found at {self.video_path}")

    def save(self):
        # Создаём бекап перед перезаписью
        self.backup_manager.create_backup(self.video_path)
        with open(self.video_path, 'w', encoding='utf-8') as f:
            vdf.dump(self.data, f, pretty=True)

    def restore_backup(self) -> bool:
        return self.backup_manager.restore_latest(self.video_path)

    def set_setting(self, key: str, value):
        if "Video" not in self.data:
            self.data["Video"] = {}
        self.data["Video"][key] = value

    def get_setting(self, key: str):
        return self.data.get("Video", {}).get(key)

    def apply_preset(self, preset: dict):
        for key, value in preset.items():
            self.set_setting(key, value)
        self.save()