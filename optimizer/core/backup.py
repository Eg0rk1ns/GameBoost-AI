import shutil
from pathlib import Path
from datetime import datetime

class BackupManager:
    def __init__(self, backup_dir: Path = None):
        self.backup_dir = backup_dir or Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    def _get_backup_name(self, file_path: Path) -> str:
        # Создаём имя бекапа из полного пути, заменяя разделители на подчёркивания
        parts = list(file_path.parts)
        # Убираем диск (например, "D:")
        if parts and ':' in parts[0]:
            parts = parts[1:]
        name_parts = []
        for p in parts:
            if p:
                name_parts.append(p)
        base = "_".join(name_parts)
        # Добавляем дату/время
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base}_{timestamp}{file_path.suffix}"

    def create_backup(self, file_path: Path) -> Path:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        backup_file = self.backup_dir / self._get_backup_name(file_path)
        shutil.copy2(file_path, backup_file)
        return backup_file

    def restore_latest(self, file_path: Path) -> bool:
        # Ищем бекапы, которые начинаются с основы пути файла
        parts = list(file_path.parts)
        if parts and ':' in parts[0]:
            parts = parts[1:]
        name_parts = []
        for p in parts:
            if p:
                name_parts.append(p)
        base = "_".join(name_parts)
        pattern = f"{base}_*{file_path.suffix}"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        if not backups:
            return False
        latest = backups[0]
        shutil.copy2(latest, file_path)
        return True

    def list_backups(self, file_path: Path) -> list:
        parts = list(file_path.parts)
        if parts and ':' in parts[0]:
            parts = parts[1:]
        name_parts = []
        for p in parts:
            if p:
                name_parts.append(p)
        base = "_".join(name_parts)
        pattern = f"{base}_*{file_path.suffix}"
        return sorted(self.backup_dir.glob(pattern), reverse=True)
