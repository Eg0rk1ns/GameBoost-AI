import os
from pathlib import Path

def get_steam_path():
    default_paths = [
        Path("C:/Program Files (x86)/Steam"),
        Path("D:/Steam"),
        Path("E:/Steam"),
        Path("C:/Steam"),
        Path("D:/Program Files (x86)/Steam"),
        Path("E:/Program Files (x86)/Steam"),
        Path("C:/Games/Steam"),
        Path("D:/Games/Steam"),
        Path("C:/Program Files/Steam"),
    ]
    for p in default_paths:
        if p.exists():
            return p
    return None

def get_steam_libraries():
    default_paths = [
        Path("C:/Program Files (x86)/Steam"),
        Path("D:/Steam"),
        Path("E:/Steam"),
        Path("C:/Steam"),
        Path("D:/Program Files (x86)/Steam"),
        Path("E:/Program Files (x86)/Steam"),
        Path("C:/Games/Steam"),
        Path("D:/Games/Steam"),
        Path("C:/Program Files/Steam"),
        Path("C:/SteamLibrary"),
        Path("D:/SteamLibrary"),
    ]
    libraries = []
    for p in default_paths:
        if p.exists():
            libraries.append(p)

    steam_env = os.environ.get("STEAM_PATH")
    if steam_env:
        p = Path(steam_env)
        if p.exists():
            libraries.append(p)

    return libraries

def get_steam_userdata_path():
    steam_path = get_steam_path()
    if steam_path:
        userdata_path = steam_path / "userdata"
        if userdata_path.exists():
            return userdata_path
    return None

def find_all_dota2_video_txt():
    userdata = get_steam_userdata_path()
    if not userdata:
        print("[DEBUG] userdata not found")
        return []
    results = []
    for user_dir in userdata.iterdir():
        if user_dir.is_dir():
            dota_cfg = user_dir / "570" / "local" / "cfg" / "video.txt"
            if dota_cfg.exists():
                # Получаем имя аккаунта из loginusers.vdf
                login_vdf = userdata.parent / "config" / "loginusers.vdf"
                account_name = user_dir.name
                if login_vdf.exists():
                    try:
                        import vdf
                        with open(login_vdf, 'r', encoding='utf-8') as f:
                            data = vdf.loads(f.read())
                        users = data.get("users", {})
                        # Ищем пользователя с ключом, равным Steam ID
                        if user_dir.name in users:
                            user_info = users[user_dir.name]
                            account_name = user_info.get("AccountName") or user_info.get("PersonaName") or user_dir.name
                        else:
                            # Если не нашли, попробуем по AccountID
                            for uid, info in users.items():
                                if info.get("AccountID") == user_dir.name:
                                    account_name = info.get("AccountName") or info.get("PersonaName") or uid
                                    break
                    except Exception as e:
                        print(f"[DEBUG] Failed to read loginusers.vdf: {e}")
                results.append({
                    "steam_id": user_dir.name,
                    "account_name": account_name,
                    "video_path": dota_cfg,
                    "game_path": None
                })
                print(f"[DEBUG] Found Dota 2 account: {account_name} ({user_dir.name})")
    if not results:
        print("[DEBUG] No Dota 2 accounts found in userdata")
    return results
