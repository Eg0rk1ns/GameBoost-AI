import os
from pathlib import Path

def find_dota2_path() -> Path | None:
    """Автоматически определяет путь к папке game/dota для Dota 2."""
    steam_paths = [
        Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Steam',
        Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)')) / 'Steam',
        Path('C:/Steam'),
        Path('D:/Steam'),
        Path('E:/Steam'),
    ]
    for sp in steam_paths:
        dota_folder = sp / 'steamapps/common/dota 2 beta/game/dota'
        if dota_folder.exists():
            return dota_folder
    return None

def find_cs2_path() -> Path | None:
    """Автоматически определяет путь к папке game/csgo для CS2."""
    steam_paths = [
        Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Steam',
        Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)')) / 'Steam',
        Path('C:/Steam'),
        Path('D:/Steam'),
        Path('E:/Steam'),
    ]
    for sp in steam_paths:
        csgo_folder = sp / 'steamapps/common/Counter-Strike Global Offensive/game/csgo'
        if csgo_folder.exists():
            return csgo_folder
    return None

def find_game_path(game_name: str) -> Path | None:
    """Универсальная функция поиска пути по имени игры."""
    if game_name.lower() == "dota 2":
        return find_dota2_path()
    elif game_name.lower() == "cs2":
        return find_cs2_path()
    else:
        return None