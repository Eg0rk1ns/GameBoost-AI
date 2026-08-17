import dearpygui.dearpygui as dpg
from pathlib import Path

class GamePanel:
    def __init__(self, game_data, container):
        self.game = game_data
        self.container = container
        self.widgets = {}
        self.autoexec_path = None

        if self.game.get("path") and (self.game.get("use_autoexec_only", False) or self.game.get("autoexec_only", False)):
            game_path = self.game["path"]
            if isinstance(game_path, str):
                game_path = Path(game_path)
            self.autoexec_path = game_path / "cfg" / "autoexec.cfg"
            print(f"[DEBUG] autoexec path: {self.autoexec_path}")
        else:
            print("[DEBUG] Game path or autoexec flag missing")

        # Все параметры
        self.params = [
            # Graphics
            {"group": "Graphics", "key": "gpu_mem_level", "label": "Texture Quality", "type": "dropdown", "options": ["Low", "Medium", "High"], "default": "Medium", "values": {"Low": "0", "Medium": "1", "High": "2"}},
            {"group": "Graphics", "key": "gpu_level", "label": "Graphics Quality", "type": "dropdown", "options": ["Low", "Medium", "High", "Ultra"], "default": "Medium", "values": {"Low": "0", "Medium": "1", "High": "2", "Ultra": "3"}},
            {"group": "Graphics", "key": "cl_globallight_shadow_mode", "label": "Shadow Quality", "type": "dropdown", "options": ["Low", "Medium", "High"], "default": "Medium", "values": {"Low": "0", "Medium": "1", "High": "2"}},
            {"group": "Graphics", "key": "r_ssao", "label": "Ambient Occlusion (SSAO)", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_deferred_specular", "label": "Specular Reflections", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_deferred_specular_bloom", "label": "Bloom", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_deferred_additive_pass", "label": "Additional Lighting", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "dota_cheap_water", "label": "High Quality Water", "type": "checkbox", "default": False},
            {"group": "Graphics", "key": "r_deferred_height_fog", "label": "Height Fog", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_dota_fxaa", "label": "FXAA Anti-Aliasing", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_dota_normal_maps", "label": "Normal Maps", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "dota_ambient_creatures", "label": "Ambient Creatures (Fauna)", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "dota_ambient_cloth", "label": "Cloth Simulation", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_grass_quality", "label": "Grass Quality", "type": "dropdown", "options": ["Off", "On"], "default": "On", "values": {"Off": "0", "On": "1"}},
            {"group": "Graphics", "key": "r_dota_allow_wind_on_trees", "label": "Tree Animation", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "r_depth_of_field", "label": "Depth of Field", "type": "checkbox", "default": False},
            {"group": "Graphics", "key": "dota_portrait_animate", "label": "Animated Portraits", "type": "checkbox", "default": True},
            {"group": "Graphics", "key": "cl_particle_fallback_base", "label": "Particle Quality", "type": "dropdown", "options": ["Low", "Medium", "High"], "default": "Medium", "values": {"Low": "0", "Medium": "1", "High": "2"}},
            # Performance
            {"group": "Performance", "key": "fps_max", "label": "Max FPS", "type": "slider", "min": 0, "max": 300, "default": 120},
            {"group": "Performance", "key": "mat_vsync", "label": "Vertical Sync (VSync)", "type": "checkbox", "default": False},
        ]

        self.render()

    def render(self):
        panel_tag = f"panel_{self.game['id']}"
        if dpg.does_item_exist(panel_tag):
            dpg.delete_item(panel_tag)

        with dpg.group(parent=self.container, tag=panel_tag):
            dpg.add_text(f"Settings for {self.game['name']}", color=(255, 200, 100))
            if self.game.get("path"):
                dpg.add_text(f"Game path: {self.game['path']}", color=(200, 200, 200))
            dpg.add_spacer(height=10)

            if self.autoexec_path:
                if self.autoexec_path.exists():
                    dpg.add_text(f"✅ autoexec.cfg found", color=(0, 255, 0))
                else:
                    dpg.add_text(f"❌ autoexec.cfg not found – will create on apply", color=(255, 0, 0))
            else:
                dpg.add_text("❌ autoexec path not set", color=(255, 0, 0))

            dpg.add_spacer(height=15)
            dpg.add_text("───────────────── Graphics ─────────────────", color=(200, 200, 255))

            current_group = None
            for param in self.params:
                if param["group"] != current_group:
                    current_group = param["group"]
                    if current_group != "Graphics":
                        dpg.add_spacer(height=10)
                        dpg.add_text(f"───────────────── {current_group} ─────────────────", color=(200, 200, 255))
                self._add_widget(param)

            dpg.add_spacer(height=20)
            dpg.add_button(label="Apply Settings", callback=self.apply_settings)

            dpg.add_text("", tag="status_text")

    def _add_widget(self, param):
        key = param["key"]
        label = param["label"]
        ptype = param["type"]
        default = param["default"]

        with dpg.group(horizontal=True):
            dpg.add_text(label)   # width удалён
            if ptype == "checkbox":
                widget = dpg.add_checkbox(default_value=default, tag=f"w_{key}")
            elif ptype == "dropdown":
                widget = dpg.add_combo(param["options"], default_value=default, tag=f"w_{key}")
            elif ptype == "slider":
                widget = dpg.add_slider_int(min_value=param["min"], max_value=param["max"], default_value=default, tag=f"w_{key}")
            else:
                widget = dpg.add_input_text(default_value=str(default), tag=f"w_{key}")
            self.widgets[key] = widget
            dpg.add_button(label="?", callback=lambda s, a, u=key: dpg.set_value("status_text", f"Tooltip for {u}"))

    def apply_settings(self):
        if not self.autoexec_path:
            dpg.set_value("status_text", "Error: autoexec path not set")
            return

        try:
            content = "// Auto-generated by GameBoost AI\n"
            for param in self.params:
                key = param["key"]
                widget = self.widgets.get(key)
                if not widget:
                    continue
                val = dpg.get_value(widget)
                if param["type"] == "checkbox":
                    val_str = "1" if val else "0"
                elif param["type"] == "dropdown":
                    if "values" in param:
                        val_str = param["values"].get(val, str(val))
                    else:
                        val_str = str(val)
                else:
                    val_str = str(val)
                content += f"{key} {val_str}\n"

            self.autoexec_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.autoexec_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)

            if self.autoexec_path.exists():
                dpg.set_value("status_text", f"✅ autoexec.cfg updated! Restart Dota 2 to see changes.")
                print(f"[DEBUG] Updated autoexec.cfg with {len(self.params)} settings")
            else:
                dpg.set_value("status_text", "❌ Failed to create autoexec.cfg")

        except PermissionError:
            dpg.set_value("status_text", "❌ Permission denied. Run as Administrator.")
            print("[ERROR] Permission denied")
        except Exception as e:
            dpg.set_value("status_text", f"❌ Error: {e}")
            print(f"[ERROR] {e}")