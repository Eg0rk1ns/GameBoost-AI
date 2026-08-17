import dearpygui.dearpygui as dpg
from optimizer.core.game_manager import GameManager
from optimizer.anticheat.detector import AntiCheatDetector
from optimizer.system.tweaks import is_admin

class OptimizerGUI:
    # Версия приложения
    VERSION = "1.0.0"
    # Данные для GitHub (замените на свои, если другие)
    REPO_OWNER = "Eg0rk1ns"
    REPO_NAME = "GameBoost-AI"

    def __init__(self):
        self.game_manager = GameManager()
        self.current_game = None
        self.anticheat_detector = AntiCheatDetector()
        self.setup_gui()

    def setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title=f"GameBoost AI Optimizer v{self.VERSION}", width=700, height=650)

        with dpg.window(label="Main Window", width=680, height=630):
            # Проверка прав администратора
            if not is_admin():
                dpg.add_text("⚠️ Run as administrator for full functionality (force close).", color=(255, 200, 0))
                dpg.add_spacer(height=10)

            dpg.add_text("Select game:")
            game_names = [g["name"] for g in self.game_manager.get_games()]
            if game_names:
                dpg.add_combo(game_names, default_value=game_names[0], tag="game_combo", callback=self.on_game_selected)
                dpg.add_spacer(height=10)

                self.current_game = self.game_manager.get_game_instance(game_names[0])
                if self.current_game:
                    try:
                        self.current_game.load()
                    except Exception as e:
                        print(f"Load error: {e}")

                dpg.add_text("Select preset:")
                presets = ["Performance", "Balanced", "Quality"]
                dpg.add_combo(presets, default_value=presets[0], tag="preset_combo")
                dpg.add_spacer(height=10)

                dpg.add_button(label="Apply preset", callback=self.apply_preset)
                dpg.add_button(label="Restore backup", callback=self.restore_backup)
                dpg.add_spacer(height=10)

                dpg.add_text("System Tweaks:")
                dpg.add_button(label="Set High Performance Power Plan", callback=self.set_power_plan)
                dpg.add_button(label="Close Background Apps (gentle)", callback=self.close_background_apps)
                dpg.add_button(label="Close Background Apps (force)", callback=self.close_background_apps_force)
                dpg.add_spacer(height=10)

                # Блок обновлений
                dpg.add_text("Updates:")
                dpg.add_button(label="Check for updates", callback=self.check_for_updates)
                dpg.add_spacer(height=10)

                # Блок статуса античитов
                dpg.add_text("Anti-Cheat Status:")
                dpg.add_text("", tag="anticheat_text")
                dpg.add_spacer(height=5)
                dpg.add_button(label="Refresh anti-cheat status", callback=self.refresh_anticheat_status)
                dpg.add_spacer(height=10)

                dpg.add_text("Status: ready", tag="status_text")
                self.update_anticheat_status()
            else:
                dpg.add_text("No games found. Please install a supported game.")

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def on_game_selected(self):
        game_name = dpg.get_value("game_combo")
        game_data = self.game_manager.get_game_by_name(game_name)
        if game_data:
            self.current_game = game_data["instance"]
            try:
                self.current_game.load()
                dpg.set_value("status_text", f"Game '{game_name}' loaded successfully")
            except Exception as e:
                dpg.set_value("status_text", f"Load error: {e}")
        self.update_anticheat_status()

    def apply_preset(self):
        if not self.current_game:
            dpg.set_value("status_text", "No game selected")
            return

        preset_name = dpg.get_value("preset_combo")
        presets_map = {
            "Performance": {
                "setting.gpu_mem_level": "0",
                "setting.graphics_quality": "0",
                "setting.shadow_quality": "0",
                "setting.vsync": "0",
                "setting.fps_max": "0"
            },
            "Balanced": {
                "setting.gpu_mem_level": "1",
                "setting.graphics_quality": "1",
                "setting.shadow_quality": "1",
                "setting.vsync": "1",
                "setting.fps_max": "120"
            },
            "Quality": {
                "setting.gpu_mem_level": "2",
                "setting.graphics_quality": "2",
                "setting.shadow_quality": "2",
                "setting.vsync": "1",
                "setting.fps_max": "144"
            }
        }
        preset = presets_map.get(preset_name)
        if preset is None:
            dpg.set_value("status_text", "Unknown preset")
            return

        try:
            self.current_game.apply_preset(preset)
            dpg.set_value("status_text", f"Preset '{preset_name}' applied successfully!")
            self.update_anticheat_status()
        except Exception as e:
            dpg.set_value("status_text", f"Error: {e}")

    def restore_backup(self):
        if not self.current_game:
            dpg.set_value("status_text", "No game selected")
            return
        try:
            if self.current_game.restore_backup():
                dpg.set_value("status_text", "Backup restored successfully!")
            else:
                dpg.set_value("status_text", "No backup found to restore")
            self.update_anticheat_status()
        except Exception as e:
            dpg.set_value("status_text", f"Restore error: {e}")

    def update_anticheat_status(self):
        self.anticheat_detector.detect()
        status = self.anticheat_detector.get_status_text()
        if dpg.does_item_exist("anticheat_text"):
            dpg.set_value("anticheat_text", status)
        if dpg.does_item_exist("status_text"):
            dpg.set_value("status_text", f"Anti-cheat: {status}")

    def refresh_anticheat_status(self):
        self.update_anticheat_status()

    def set_power_plan(self):
        from optimizer.system.tweaks import SystemTweaks
        if SystemTweaks.set_high_performance_power_plan():
            dpg.set_value("status_text", "Power plan set to High Performance")
        else:
            dpg.set_value("status_text", "Failed to set power plan")

    def close_background_apps(self):
        from optimizer.system.tweaks import SystemTweaks
        closed, failed, not_found = SystemTweaks.close_background_apps()
        msg = "No apps closed"
        if closed:
            msg = f"Closed: {len(closed)} apps (e.g., {', '.join(closed[:3])}...)"
        if failed:
            msg += f" | Failed: {len(failed)}"
        if not_found:
            msg += f" | Not running: {len(not_found)}"
        dpg.set_value("status_text", msg)

    def close_background_apps_force(self):
        from optimizer.system.tweaks import SystemTweaks
        closed, failed, failed_admin, not_found, not_admin = SystemTweaks.close_background_apps_force()
        if not_admin:
            dpg.set_value("status_text", "Run as administrator to force close all apps")
            return
        msg = "No apps closed"
        if closed:
            msg = f"Force closed: {len(closed)} apps (e.g., {', '.join(closed[:3])}...)"
        if failed:
            msg += f" | Failed: {len(failed)}"
        if failed_admin:
            msg += f" | Requires admin: {len(failed_admin)} (run as administrator)"
        if not_found:
            msg += f" | Not running: {len(not_found)}"
        dpg.set_value("status_text", msg)

    def check_for_updates(self):
        from optimizer.updater.checker import UpdateChecker
        from optimizer.updater.installer import UpdaterInstaller
        from pathlib import Path
        import sys

        dpg.set_value("status_text", "Checking for updates...")
        checker = UpdateChecker(self.REPO_OWNER, self.REPO_NAME, self.VERSION)
        has_update, latest_version, download_url = checker.check_for_update()

        if has_update and download_url:
            dpg.set_value("status_text", f"New version {latest_version} available! Downloading...")
            # Скачиваем обновление в текущую директорию (можно изменить)
            update_file = UpdaterInstaller.download_update(
                download_url,
                Path(".")
            )
            if update_file:
                dpg.set_value("status_text", f"Update downloaded to {update_file}. Installing...")
                # Определяем папку приложения
                if getattr(sys, 'frozen', False):
                    app_dir = Path(sys.executable).parent
                else:
                    app_dir = Path(".").resolve()
                if UpdaterInstaller.install_update(update_file, app_dir):
                    dpg.set_value("status_text", "Update installed. Please restart the application.")
                else:
                    dpg.set_value("status_text", "Installation failed.")
            else:
                dpg.set_value("status_text", "Download failed.")
        else:
            if has_update:
                dpg.set_value("status_text", "New version available, but no download link found.")
            else:
                dpg.set_value("status_text", "You are using the latest version.")