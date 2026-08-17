import dearpygui.dearpygui as dpg
import json
from pathlib import Path
from optimizer.core.game_detector import detect_games
from optimizer.gui.game_panel import GamePanel

class MainWindow:
    def __init__(self):
        self.games_db = self.load_games_db()
        self.found_games = detect_games(self.games_db)
        self.current_game = None
        self.game_panel = None
        self.setup_gui()

    def load_games_db(self):
        db_path = Path(__file__).parent.parent / "core" / "games_db.json"
        print(f"[DEBUG] Loading games_db from: {db_path}")
        print(f"[DEBUG] File exists: {db_path.exists()}")
        try:
            with open(db_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                print(f"[DEBUG] Loaded {len(data.get('games', []))} games from DB")
                return data["games"]
        except Exception as e:
            print(f"[ERROR] Failed to load games_db: {e}")
            return []

    def setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title="GameBoost AI", width=1000, height=700)

        with dpg.window(label="GameBoost AI", width=980, height=680, tag="main_window"):
            with dpg.group(horizontal=True):
                # Левая панель – библиотека
                with dpg.child_window(width=250, tag="library_panel"):
                    dpg.add_text("Library")
                    dpg.add_spacer(height=10)

                    found_games = [g for g in self.found_games if g.get("found", False)]
                    not_found = [g for g in self.found_games if not g.get("found", False)]

                    for game in found_games:
                        with dpg.group(horizontal=True):
                            dpg.add_text(game["icon"], color=(255, 255, 0))
                            dpg.add_button(label=game["name"], callback=self.on_game_selected, user_data=game["id"], width=-1)

                    if not_found:
                        dpg.add_spacer(height=10)
                        dpg.add_text("Not installed:", color=(150, 150, 150))
                        for game in not_found:
                            with dpg.group(horizontal=True):
                                dpg.add_text(game["icon"], color=(100, 100, 100))
                                dpg.add_text(game["name"], color=(150, 150, 150))

                    dpg.add_spacer(height=20)
                    dpg.add_button(label="+ Add Game", callback=self.add_game_manually)

                # Правая панель – контейнер для настроек игры
                with dpg.child_window(tag="game_panel_container", width=-1):
                    dpg.add_text("Select a game from the library", tag="game_panel_placeholder")

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def on_game_selected(self, sender, app_data, user_data):
        game_id = user_data
        game_data = next((g for g in self.found_games if g["id"] == game_id), None)
        if not game_data:
            return
        if not game_data.get("found", False):
            # Показываем сообщение в статусе (но у нас нет статуса, поэтому выведем в консоль)
            print("Game not installed. Please install it first.")
            return
        self.current_game = game_data
        # Очищаем правую панель
        dpg.delete_item("game_panel_container", children_only=True)
        # Создаём панель игры
        self.game_panel = GamePanel(game_data, container="game_panel_container")
        self.game_panel.render()   # <-- вызов render для отображения

    def add_game_manually(self):
        # Заглушка
        print("Manual add will be implemented later")