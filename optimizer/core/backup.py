import shutil
from pathlib import Path
from datetime import datetime

class BackupManager:
    def __init__(self, game_path: Path, backup_dir: Path = None):
        self.game_path = game_path
        self.backup_dir = backup_dir or Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    def _get_backup_name(self, file_path: Path) -> str:
        rel_path = file_path.relative_to(self.game_path)
        # Объединяем все части пути (без расширения) через подчёркивание
        base_name = "_".join(rel_path.with_suffix('').parts)
        suffix = rel_path.suffix
        return f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"

    def create_backup(self, file_path: Path) -> Path:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        backup_file = self.backup_dir / self._get_backup_name(file_path)
        shutil.copy2(file_path, backup_file)
        return backup_file

    def restore_latest(self, file_path: Path) -> bool:
        rel_path = file_path.relative_to(self.game_path)
        base_name = "_".join(rel_path.with_suffix('').parts)
        pattern = f"{base_name}_*{rel_path.suffix}"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        if not backups:
            return False
        latest = backups[0]
        shutil.copy2(latest, file_path)
        return True

    def list_backups(self, file_path: Path) -> list:
        rel_path = file_path.relative_to(self.game_path)
        base_name = "_".join(rel_path.with_suffix('').parts)
        pattern = f"{base_name}_*{rel_path.suffix}"
        return sorted(self.backup_dir.glob(pattern), reverse=True)