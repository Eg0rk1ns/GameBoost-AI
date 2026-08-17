import psutil
from typing import Dict

# Словарь соответствия процессов → название античита
PROCESS_MAP = {
    "BEService.exe": "BattlEye",
    "EasyAntiCheat.exe": "Easy Anti-Cheat",
    "EasyAntiCheat_Setup.exe": "Easy Anti-Cheat",
    "eac_server.exe": "Easy Anti-Cheat (server)",
    "Vanguard.exe": "Riot Vanguard",
    "vgc.exe": "Riot Vanguard (service)",
    "FaceitAC.exe": "FACEIT Anti-Cheat",
    "FaceitService.exe": "FACEIT Anti-Cheat (service)",
    "EOSAntiCheat.exe": "Epic Online Services Anti-Cheat",
    "EOSAC.exe": "Epic Online Services Anti-Cheat",
    "PnkBstrA.exe": "PunkBuster (A)",
    "PnkBstrB.exe": "PunkBuster (B)",
    "GameGuard.des": "nProtect GameGuard",
    "XIGNCODE3.exe": "XIGNCODE3",
    "byfron_anti_cheat.exe": "Byfron (Roblox)",
    "valve-anticheat.exe": "Valve Anti-Cheat (legacy)",
}

# Словарь драйверов (опционально, для более точного обнаружения)
DRIVER_MAP = {
    "BEDaisy.sys": "BattlEye",
    "EasyAntiCheat.sys": "Easy Anti-Cheat",
    "vanguard.sys": "Riot Vanguard",
    "faceit.sys": "FACEIT Anti-Cheat",
    "EOSAntiCheat.sys": "Epic Online Services Anti-Cheat",
    "PnkBstrA.sys": "PunkBuster",
    "PnkBstrB.sys": "PunkBuster",
}

class AntiCheatDetector:
    def __init__(self):
        self.detected = {}

    def detect(self) -> Dict[str, str]:
        """
        Сканирует запущенные процессы и драйверы.
        Возвращает словарь {имя_античита: статус} где статус "running" или "driver".
        """
        result = {}
        # Проверяем процессы
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name in PROCESS_MAP:
                    anticheat_name = PROCESS_MAP[proc_name]
                    result[anticheat_name] = "running"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Проверяем драйверы (требуются права администратора)
        try:
            import wmi
            c = wmi.WMI()
            for driver in c.Win32_SystemDriver():
                if driver.Name in DRIVER_MAP:
                    anticheat_name = DRIVER_MAP[driver.Name]
                    if anticheat_name not in result:
                        result[anticheat_name] = "driver"
        except:
            # WMI может быть недоступен или нет прав
            pass

        self.detected = result
        return result

    def is_running(self, name: str) -> bool:
        """Проверяет, активен ли конкретный античит"""
        return name in self.detected and self.detected[name] in ("running", "driver")

    def get_status_text(self) -> str:
        """Возвращает краткий текст для отображения в GUI"""
        if not self.detected:
            return "No anti-cheats detected"
        active = [f"{name} ({status})" for name, status in self.detected.items()]
        return "Active: " + ", ".join(active)