from pathlib import Path
from typing import List, Optional
from optimizer.games.base import Game

class GameManager:
    def __init__(self):
        self.games = []
        self._discover_games()

    def _discover_games(self):
        from optimizer.games.dota2.dota2_game import Dota2Game
        from optimizer.games.cs2.cs2_game import CS2Game
        from optimizer.games.rust.rust_game import RustGame 

        game_classes = [Dota2Game, CS2Game, RustGame]  
        for game_class in game_classes:
            path = game_class.detect()
            if path:
                self.games.append({
                    "name": game_class.get_name(),
                    "path": path,
                    "class": game_class,
                    "instance": game_class(path)
                })

    def get_games(self) -> List[dict]:
        return self.games

    def get_game_by_name(self, name: str) -> Optional[dict]:
        for game in self.games:
            if game["name"] == name:
                return game
        return None

    def get_game_instance(self, name: str) -> Optional[Game]:
        game = self.get_game_by_name(name)
        if game:
            return game["instance"]
        return None