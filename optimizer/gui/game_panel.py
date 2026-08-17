import dearpygui.dearpygui as dpg
from pathlib import Path
from optimizer.core.performance_predictor import PerformancePredictor

class GamePanel:
    def __init__(self, game_data, container):
        self.game = game_data
        self.container = container
        self.settings_widgets = {}
        self.autoexec_path = None
        self.status_tag = "status_text"
        self.base_fps = 120
        self.predictor = PerformancePredictor()

        if self.game.get("path") and self.game.get("autoexec_only", False):
            game_path = self.game["path"]
            if isinstance(game_path, str):
                game_path = Path(game_path)
            self.autoexec_path = game_path / "cfg" / "autoexec.cfg"
            print(f"[DEBUG] autoexec path: {self.autoexec_path}")
            print(f"[DEBUG] File exists? {self.autoexec_path.exists()}")
        else:
            print("[DEBUG] Game path or autoexec flag missing")

        self.plot_tag = "perf_drawlist"
        self.current_fps_text = "current_fps_text"
        self.predicted_fps_text = "predicted_fps_text"

    def render(self):
        panel_tag = f"panel_{self.game['id']}"
        if dpg.does_item_exist(panel_tag):
            dpg.delete_item(panel_tag)

        with dpg.group(parent=self.container, tag=panel_tag):
            dpg.add_text(f"Settings for {self.game['name']}", color=(255, 200, 100))
            if self.game.get("path"):
                dpg.add_text(f"Game path: {self.game['path']}", color=(200, 200, 200))
            dpg.add_spacer(height=10)

            if self.autoexec_path and self.autoexec_path.exists():
                dpg.add_text(f"✅ autoexec.cfg found", color=(0, 255, 0))
            else:
                dpg.add_text(f"❌ autoexec.cfg not found", color=(255, 0, 0))
            dpg.add_spacer(height=10)

            # --- Прогноз производительности (Pro) ---
            with dpg.collapsing_header(label="📊 Performance Prediction (Pro)", default_open=True):
                with dpg.drawlist(width=300, height=120, tag=self.plot_tag):
                    pass
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text("Current FPS: ", color=(200, 200, 200))
                    dpg.add_text(str(self.base_fps), tag=self.current_fps_text, color=(255, 255, 255))
                    dpg.add_text("    Predicted FPS: ", color=(200, 200, 200))
                    dpg.add_text(str(self.base_fps), tag=self.predicted_fps_text, color=(0, 255, 0))
                dpg.add_button(label="Set base FPS", callback=self.set_base_fps)

            dpg.add_spacer(height=10)

            self._add_graphics_group()
            self._add_performance_group()
            self._add_network_group()
            self._add_interface_group()
            self._add_system_group()

            dpg.add_spacer(height=15)
            dpg.add_button(label="✅ Apply Settings", callback=self.apply_settings, width=-1)
            dpg.add_spacer(height=5)
            dpg.add_text("", tag=self.status_tag)

    # ---------- Группы настроек ----------
    def _add_graphics_group(self):
        with dpg.collapsing_header(label="🎮 Graphics", default_open=True):
            with dpg.group(horizontal=True):
                with dpg.group():
                    self._add_dropdown("Texture Quality", "gpu_mem_level", ["Low", "Medium", "High"], default=1)
                    self._add_dropdown("Graphics Quality", "gpu_level", ["Low", "Medium", "High", "Ultra"], default=1)
                    self._add_dropdown("Shadow Quality", "cl_globallight_shadow_mode", ["Low", "Medium", "High"], default=1)
                    self._add_dropdown("Particle Quality", "cl_particle_fallback_base", ["Low", "Medium", "High", "Ultra"], default=2)
                    self._add_dropdown("Grass Quality", "r_grass_quality", ["Off", "Low", "Medium", "High", "Ultra"], default=1)
                with dpg.group():
                    self._add_checkbox("Ambient Occlusion", "r_ssao", default=True)
                    self._add_checkbox("Specular Reflections", "r_deferred_specular", default=True)
                    self._add_checkbox("Bloom", "r_deferred_specular_bloom", default=True)
                    self._add_checkbox("Additional Lighting", "r_deferred_additive_pass", default=True)
                    self._add_checkbox("High Quality Water", "dota_cheap_water", default=True, invert=True)
                    self._add_checkbox("Height Fog", "r_deferred_height_fog", default=True)
                    self._add_checkbox("FXAA", "r_dota_fxaa", default=True)
                    self._add_checkbox("Normal Maps", "r_dota_normal_maps", default=True)
                    self._add_checkbox("Ambient Creatures", "dota_ambient_creatures", default=True)
                    self._add_checkbox("Cloth Simulation", "dota_ambient_cloth", default=True)
                    self._add_checkbox("Tree Animation", "r_dota_allow_wind_on_trees", default=True)
                    self._add_checkbox("Depth of Field", "r_depth_of_field", default=False)
                    self._add_checkbox("Animated Portraits", "dota_portrait_animate", default=True)

    def _add_performance_group(self):
        with dpg.collapsing_header(label="⚡ Performance", default_open=True):
            self._add_slider("Max FPS", "fps_max", min=0, max=300, default=120)
            self._add_checkbox("Vertical Sync (VSync)", "mat_vsync", default=False)

    def _add_network_group(self):
        with dpg.collapsing_header(label="🌐 Network", default_open=False):
            self._add_slider_float("Interpolation", "cl_interp", min=0.0, max=0.1, default=0.031, step=0.001)
            self._add_slider("Cmdrate", "cl_cmdrate", min=30, max=128, default=64)
            self._add_slider("Updaterate", "cl_updaterate", min=30, max=128, default=64)
            self._add_slider("Rate", "rate", min=40000, max=100000, default=80000)
            self._add_checkbox("Net Graph", "net_graph", default=False)

    def _add_interface_group(self):
        with dpg.collapsing_header(label="🎮 Interface & Controls", default_open=False):
            self._add_checkbox("Right Click Deny", "dota_force_right_click_attack", default=True)
            self._add_checkbox("Disable Range Finder", "dota_disable_range_finder", default=False)
            self._add_slider("Camera Acceleration", "dota_camera_accelerate", min=0, max=100, default=49)
            self._add_checkbox("Screen Shake", "dota_screen_shake", default=False)
            self._add_slider("Minimap Hero Size", "dota_minimap_hero_size", min=300, max=1500, default=700)
            self._add_slider_float("Minimap Click Delay", "dota_minimap_misclick_time", min=0, max=1, default=0, step=0.1)
            self._add_slider("Health Per Vertical Marker", "dota_health_per_vertical_marker", min=1, max=1000, default=250)
            self._add_slider("Health Bars", "dota_hud_healthbars", min=0, max=3, default=3)

    def _add_system_group(self):
        with dpg.collapsing_header(label="🛠️ System Tweaks", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_button(label="⚡ High Performance", callback=self.set_power_plan)
                dpg.add_button(label="🧹 Close Apps (gentle)", callback=self.close_background_apps)
                dpg.add_button(label="💥 Close Apps (force)", callback=self.close_background_apps_force)
            dpg.add_spacer(height=5)
            dpg.add_text("Steam Launch Options:", color=(200, 200, 200))
            self._add_checkbox("-high (High Priority)", "launch_high", default=False)
            self._add_checkbox("-novid (Skip Intro)", "launch_novid", default=False)
            self._add_checkbox("-nojoy (Disable Joysticks)", "launch_nojoy", default=False)
            self._add_checkbox("-console (Open Console)", "launch_console", default=False)
            self._add_checkbox("-dx11 (DirectX 11)", "launch_dx11", default=False)
            self._add_checkbox("-vulkan", "launch_vulkan", default=False)
            self._add_checkbox("-prewarm", "launch_prewarm", default=False)
            self._add_checkbox("-map dota", "launch_mapdota", default=False)

    # ---------- Вспомогательные методы добавления виджетов ----------
    def _add_dropdown(self, label, cmd, options, default=0):
        tag = f"{cmd}_widget"
        dpg.add_text(label)
        widget = dpg.add_combo(options, default_value=options[default], tag=tag, width=-1)
        self.settings_widgets[cmd] = {"label": label, "type": "dropdown", "cmd": cmd, "widget": widget, "options": options}
        dpg.set_item_callback(widget, self._on_setting_changed)

    def _add_checkbox(self, label, cmd, default=False, invert=False):
        tag = f"{cmd}_widget"
        dpg.add_text(label)
        widget = dpg.add_checkbox(default_value=default, tag=tag)   # <-- width убран!
        self.settings_widgets[cmd] = {"label": label, "type": "checkbox", "cmd": cmd, "widget": widget, "invert": invert}
        dpg.set_item_callback(widget, self._on_setting_changed)

    def _add_slider(self, label, cmd, min=0, max=300, default=120, step=1):
        tag = f"{cmd}_widget"
        dpg.add_text(label)
        widget = dpg.add_slider_int(min_value=min, max_value=max, default_value=default, tag=tag, width=-1)
        self.settings_widgets[cmd] = {"label": label, "type": "slider", "cmd": cmd, "widget": widget}
        dpg.set_item_callback(widget, self._on_setting_changed)

    def _add_slider_float(self, label, cmd, min=0.0, max=1.0, default=0.0, step=0.01):
        tag = f"{cmd}_widget"
        dpg.add_text(label)
        widget = dpg.add_slider_float(min_value=min, max_value=max, default_value=default, tag=tag, width=-1)
        self.settings_widgets[cmd] = {"label": label, "type": "slider_float", "cmd": cmd, "widget": widget}
        dpg.set_item_callback(widget, self._on_setting_changed)

    # ---------- Обработчик изменения настроек ----------
    def _on_setting_changed(self):
        self.update_prediction()

    # ---------- Прогноз производительности ----------
    def update_prediction(self):
        settings = {}
        for cmd, data in self.settings_widgets.items():
            if data["type"] == "button":
                continue
            widget = data["widget"]
            val = dpg.get_value(widget)

            if data["type"] == "checkbox":
                if data.get("invert", False):
                    val = 0 if val else 1
                else:
                    val = 1 if val else 0
            elif data["type"] == "dropdown":
                try:
                    idx = data["options"].index(val)
                except ValueError:
                    idx = 0
                val = str(idx)
            elif data["type"] in ("slider", "slider_float"):
                val = int(val) if isinstance(val, float) and val.is_integer() else val
            else:
                val = str(val)

            if not cmd.startswith("launch_"):
                settings[cmd] = val

        predicted = PerformancePredictor.predict_fps(settings, self.base_fps)
        dpg.set_value(self.current_fps_text, str(self.base_fps))
        dpg.set_value(self.predicted_fps_text, str(predicted))

        self.draw_performance_graph(self.base_fps, predicted)

    def draw_performance_graph(self, current_fps, predicted_fps):
        drawlist = self.plot_tag
        if not dpg.does_item_exist(drawlist):
            return
        dpg.delete_item(drawlist, children_only=True)

        width = dpg.get_item_width(drawlist) or 300
        height = dpg.get_item_height(drawlist) or 120
        max_fps = max(current_fps, predicted_fps, 1)
        max_height = height - 30

        bar_width = 60
        gap = 40
        x1 = (width - 2*bar_width - gap) // 2
        y1 = 10

        bar1_height = int((current_fps / max_fps) * max_height) if max_fps > 0 else 10
        dpg.draw_rectangle(pmin=(x1, y1 + max_height - bar1_height), pmax=(x1 + bar_width, y1 + max_height), color=(100, 100, 255), fill=(100, 100, 255))
        dpg.draw_text(pos=(x1 + 5, y1 + max_height - bar1_height - 20), text=str(current_fps), color=(255, 255, 255))

        x2 = x1 + bar_width + gap
        bar2_height = int((predicted_fps / max_fps) * max_height) if max_fps > 0 else 10
        color = (0, 255, 0) if predicted_fps >= current_fps else (255, 255, 0)
        dpg.draw_rectangle(pmin=(x2, y1 + max_height - bar2_height), pmax=(x2 + bar_width, y1 + max_height), color=color, fill=color)
        dpg.draw_text(pos=(x2 + 5, y1 + max_height - bar2_height - 20), text=str(predicted_fps), color=(255, 255, 255))

        dpg.draw_text(pos=(x1, y1 + max_height + 5), text="Current", color=(200, 200, 200))
        dpg.draw_text(pos=(x2, y1 + max_height + 5), text="Predicted", color=(200, 200, 200))

    # ---------- Системные кнопки ----------
    def set_base_fps(self):
        dpg.set_value(self.status_tag, "Base FPS set to 120 (demo)")

    def set_power_plan(self):
        from optimizer.system.tweaks import SystemTweaks
        if SystemTweaks.set_high_performance_power_plan():
            dpg.set_value(self.status_tag, "✅ Power plan set to High Performance")
        else:
            dpg.set_value(self.status_tag, "❌ Failed to set power plan")

    def close_background_apps(self):
        from optimizer.system.tweaks import SystemTweaks
        closed, failed, not_found = SystemTweaks.close_background_apps()
        msg = "✅" if closed else "❌"
        if closed:
            msg += f" Closed: {len(closed)} apps"
        if failed:
            msg += f" | Failed: {len(failed)}"
        if not_found:
            msg += f" | Not running: {len(not_found)}"
        dpg.set_value(self.status_tag, msg)

    def close_background_apps_force(self):
        from optimizer.system.tweaks import SystemTweaks
        closed, failed, failed_admin, not_found, not_admin = SystemTweaks.close_background_apps_force()
        if not_admin:
            dpg.set_value(self.status_tag, "⚠️ Run as administrator to force close")
            return
        msg = "✅" if closed else "❌"
        if closed:
            msg += f" Force closed: {len(closed)} apps"
        if failed:
            msg += f" | Failed: {len(failed)}"
        if failed_admin:
            msg += f" | Requires admin: {len(failed_admin)}"
        if not_found:
            msg += f" | Not running: {len(not_found)}"
        dpg.set_value(self.status_tag, msg)

    # ---------- Применение настроек ----------
    def apply_settings(self):
        if not self.autoexec_path:
            dpg.set_value(self.status_tag, "❌ Error: autoexec path not set")
            return

        try:
            lines = ["// Auto-generated by GameBoost AI"]
            for cmd, data in self.settings_widgets.items():
                if data["type"] == "button":
                    continue
                widget = data["widget"]
                val = dpg.get_value(widget)

                if data["type"] == "checkbox":
                    if data.get("invert", False):
                        val = "0" if val else "1"
                    else:
                        val = "1" if val else "0"
                elif data["type"] == "dropdown":
                    try:
                        idx = data["options"].index(val)
                    except ValueError:
                        idx = 0
                    val = str(idx)
                elif data["type"] in ("slider", "slider_float"):
                    val = str(val)
                else:
                    val = str(val)

                if cmd.startswith("launch_"):
                    continue
                lines.append(f"{cmd} {val}")

            launch_options = []
            for cmd, data in self.settings_widgets.items():
                if cmd.startswith("launch_") and data["type"] == "checkbox":
                    if dpg.get_value(data["widget"]):
                        launch_options.append(cmd.replace("launch_", "-"))

            content = "\n".join(lines)
            self.autoexec_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.autoexec_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)

            status_msg = f"✅ autoexec.cfg updated!"
            if launch_options:
                status_msg += f"\n💡 Add to Steam launch options: {' '.join(launch_options)}"
            dpg.set_value(self.status_tag, status_msg)
            print(f"[DEBUG] Updated autoexec.cfg at {self.autoexec_path}")
            if launch_options:
                print(f"[INFO] Recommended launch options: {' '.join(launch_options)}")

        except Exception as e:
            dpg.set_value(self.status_tag, f"❌ Error: {e}")
            print(f"[ERROR] {e}")
