import dearpygui.dearpygui as dpg
from optimizer.core.game_manager import GameManager

class OptimizerGUI:
    def __init__(self):
        self.game_manager = GameManager()
        self.current_game = None
        self.setup_gui()

    def setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title="Game Optimizer", width=700, height=500)

        with dpg.window(label="Main Window", width=680, height=480):
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
                        dpg.set_value("status_text", f"Load error: {e}")

                dpg.add_text("Select preset:")
                presets = ["Performance", "Balanced", "Quality"]
                dpg.add_combo(presets, default_value=presets[0], tag="preset_combo")
                dpg.add_spacer(height=10)

                dpg.add_button(label="Apply preset", callback=self.apply_preset)
                dpg.add_button(label="Restore backup", callback=self.restore_backup)
                dpg.add_spacer(height=10)

                dpg.add_text("Status: ready", tag="status_text")
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
        except Exception as e:
            dpg.set_value("status_text", f"Restore error: {e}")