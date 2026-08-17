import os
import sys
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path
from typing import Optional

class UpdaterInstaller:
    @staticmethod
    def download_update(url: str, dest_dir: Path) -> Optional[Path]:
        """Скачивает обновление и сохраняет во временную папку"""
        try:
            # Создаём временную папку
            temp_dir = Path(tempfile.mkdtemp(prefix="gameboost_update_"))
            # Определяем имя файла из URL
            filename = url.split("/")[-1]
            file_path = temp_dir / filename
            
            # Скачиваем с прогрессом (можно потом добавить колбэк для GUI)
            print(f"Downloading update from {url} to {file_path}")
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return file_path
        except Exception as e:
            print(f"Download failed: {e}")
            return None

    @staticmethod
    def install_update(update_file: Path, app_dir: Path) -> bool:
        """
        Устанавливает обновление.
        Если это .exe — запускает его с параметрами для тихой установки.
        Если .zip — распаковывает и заменяет файлы.
        """
        try:
            if update_file.suffix.lower() == ".exe":
                # Запускаем установщик и закрываем текущее приложение
                subprocess.Popen(
                    [str(update_file), "/SILENT", "/VERYSILENT"],
                    cwd=str(app_dir)
                )
                return True
            elif update_file.suffix.lower() == ".zip":
                # Распаковываем и заменяем файлы
                import zipfile
                with zipfile.ZipFile(update_file, 'r') as zip_ref:
                    zip_ref.extractall(app_dir)
                return True
            else:
                return False
        except Exception as e:
            print(f"Install failed: {e}")
            return False