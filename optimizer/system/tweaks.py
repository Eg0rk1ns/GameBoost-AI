import json
import subprocess
import psutil
import time
import ctypes
from pathlib import Path
from typing import List, Tuple, Set

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class SystemTweaks:
    @staticmethod
    def _load_whitelist() -> Set[str]:
        whitelist_path = Path("config/whitelist.json")
        if not whitelist_path.exists():
            whitelist_path.parent.mkdir(exist_ok=True)
            default = {
                "games": ["cs2.exe", "dota2.exe", "valorant.exe"],
                "critical": ["steam.exe", "epicgameslauncher.exe", "vgc.exe"],
                "communication": ["discord.exe", "teamspeak3.exe"],
                "peripherals": ["Razer Synapse.exe", "Logitech G Hub.exe"],
                "vpn": ["nordvpn.exe", "protonvpn.exe"],
                "streaming": ["obs64.exe"],
                "user_custom": []
            }
            with open(whitelist_path, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
        
        with open(whitelist_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        whitelist = set()
        for category in data.values():
            if isinstance(category, list):
                whitelist.update(category)
        return {item.lower() for item in whitelist}

    @staticmethod
    def set_high_performance_power_plan() -> bool:
        try:
            subprocess.run(
                "powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
                check=True, capture_output=True, shell=True
            )
            return True
        except:
            return False

    @staticmethod
    def set_process_priority(pid: int, priority: str = "high") -> bool:
        try:
            process = psutil.Process(pid)
            if priority.lower() == "high":
                process.nice(psutil.HIGH_PRIORITY_CLASS)
            elif priority.lower() == "realtime":
                process.nice(psutil.REALTIME_PRIORITY_CLASS)
            elif priority.lower() == "above_normal":
                process.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
            return True
        except:
            return False

    @staticmethod
    def close_background_apps() -> Tuple[List[str], List[str], List[str]]:
        whitelist = SystemTweaks._load_whitelist()
        targets = [
            "chrome.exe", "firefox.exe", "msedge.exe", "microsoftedge.exe",
            "brave.exe", "opera.exe", "vivaldi.exe",
            "yandex.exe", "browser.exe", "yandexbrowser.exe",
            "qbittorrent.exe", "utorrent.exe", "deluge.exe",
            "notepad++.exe", "code.exe", "sublime_text.exe",
            "skype.exe", "zoom.exe", "slack.exe", "teams.exe",
            "spotify.exe", "telegram.exe", "whatsapp.exe"
        ]
        closed = []
        failed = []
        not_found = []
        
        running_names = set()
        for proc in psutil.process_iter(['name']):
            try:
                running_names.add(proc.info['name'].lower())
            except:
                pass
        
        # Отладочный вывод: какие процессы из targets реально запущены
        print("DEBUG: Running target processes:")
        for name in sorted(running_names):
            if any(name == target.lower() for target in targets):
                print(f"  {name}")
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if proc_name in targets and proc_name not in whitelist:
                    parent = psutil.Process(proc.info['pid'])
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.kill()
                        except:
                            pass
                    parent.kill()
                    closed.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                failed.append(proc.info['name'])
            except Exception:
                failed.append(proc.info['name'])
        
        for app in targets:
            if app.lower() not in running_names:
                not_found.append(app)
        
        failed = [f for f in failed if f.lower() in running_names]
        time.sleep(1)
        return closed, failed, not_found

    @staticmethod
    def close_background_apps_force() -> Tuple[List[str], List[str], List[str], List[str], bool]:
        if not is_admin():
            return [], [], [], [], True
        
        whitelist = SystemTweaks._load_whitelist()
        targets = [
            "chrome.exe", "firefox.exe", "msedge.exe", "microsoftedge.exe",
            "brave.exe", "opera.exe", "vivaldi.exe",
            "yandex.exe", "browser.exe", "yandexbrowser.exe",
            "qbittorrent.exe", "utorrent.exe", "deluge.exe",
            "notepad++.exe", "code.exe", "sublime_text.exe",
            "skype.exe", "zoom.exe", "slack.exe", "teams.exe",
            "spotify.exe", "telegram.exe", "whatsapp.exe"
        ]
        
        running_names = set()
        for proc in psutil.process_iter(['name']):
            try:
                running_names.add(proc.info['name'].lower())
            except:
                pass
        
        # Отладочный вывод
        print("DEBUG: Running target processes (force):")
        for name in sorted(running_names):
            if any(name == target.lower() for target in targets):
                print(f"  {name}")
        
        closed = []
        failed = []
        failed_admin = []
        not_found = []
        
        for app in targets:
            app_lower = app.lower()
            if app_lower in whitelist:
                continue
            
            if app_lower not in running_names:
                not_found.append(app)
                continue
            
            try:
                result = subprocess.run(
                    f"taskkill /F /IM {app} /T",
                    capture_output=True, shell=True, text=True
                )
                if result.returncode == 0:
                    closed.append(app)
                else:
                    if "ACCESS DENIED" in result.stderr.upper() or "ОТКАЗАНО В ДОСТУПЕ" in result.stderr:
                        failed_admin.append(app)
                    else:
                        failed.append(app)
            except Exception:
                failed.append(app)
        
        return closed, failed, failed_admin, not_found, False