import os
from pathlib import Path
from optimizer.utils.steam import get_steam_libraries

def detect_games(games_db):
    found = []
    steam_libraries = get_steam_libraries()
    print(f"[DEBUG] Found Steam libraries: {steam_libraries}")

    for game in games_db:
        game_found = False
        if game.get("use_autoexec_only", False):
            for search_path in game["search_paths"]:
                for lib in steam_libraries:
                    full_path = lib / search_path
                    if full_path.exists():
                        found.append({
                            "id": game["id"],
                            "name": game["name"],
                            "icon": game["icon"],
                            "path": full_path,
                            "config_file": "cfg/autoexec.cfg",
                            "settings": game["settings"],
                            "format": "autoexec",
                            "found": True,
                            "use_autoexec_only": True,
                            "autoexec_only": True
                        })
                        game_found = True
                        print(f"[DEBUG] Found {game['name']} at {full_path} (autoexec mode)")
                        break
                if game_found:
                    break
            if not game_found:
                print(f"[DEBUG] {game['name']} not found")
                found.append({
                    "id": game["id"],
                    "name": game["name"] + " (not installed)",
                    "icon": game["icon"],
                    "path": None,
                    "config_file": None,
                    "settings": game["settings"],
                    "format": game["format"],
                    "found": False
                })
            continue

        # Обычные игры (CS2)
        for search_path in game["search_paths"]:
            for lib in steam_libraries:
                full_path = lib / search_path
                if full_path.exists():
                    found.append({
                        "id": game["id"],
                        "name": game["name"],
                        "icon": game["icon"],
                        "path": full_path,
                        "config_file": game["config_file"],
                        "settings": game["settings"],
                        "format": game["format"],
                        "found": True
                    })
                    game_found = True
                    print(f"[DEBUG] Found {game['name']} at {full_path}")
                    break
            if game_found:
                break
        if not game_found:
            print(f"[DEBUG] {game['name']} not found")
            found.append({
                "id": game["id"],
                "name": game["name"] + " (not installed)",
                "icon": game["icon"],
                "path": None,
                "config_file": None,
                "settings": game["settings"],
                "format": game["format"],
                "found": False
            })
    return found