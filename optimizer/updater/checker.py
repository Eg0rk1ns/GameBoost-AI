import json
import requests
from packaging.version import parse as parse_version
from pathlib import Path

class UpdateChecker:
    def __init__(self, repo_owner: str, repo_name: str, current_version: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    def check_for_update(self) -> tuple[bool, str | None, str | None]:
        """
        Проверяет наличие новой версии на GitHub.
        Возвращает: (есть_обновление, последняя_версия, url_для_скачивания)
        """
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code != 200:
                return False, None, None
            data = response.json()
            latest_version = data.get("tag_name", "").lstrip("v")
            if parse_version(latest_version) > parse_version(self.current_version):
                # Ищем asset с расширением .exe или .zip (зависит от вашей упаковки)
                assets = data.get("assets", [])
                download_url = None
                for asset in assets:
                    name = asset.get("name", "")
                    if name.endswith(".exe") or name.endswith(".zip"):
                        download_url = asset.get("browser_download_url")
                        break
                return True, latest_version, download_url
            return False, None, None
        except Exception:
            return False, None, None