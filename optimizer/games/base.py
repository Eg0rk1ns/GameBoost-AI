from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

class Game(ABC):
    """Абстрактный базовый класс для всех игр"""

    def __init__(self, game_path: Path):
        self.game_path = game_path
        self.config = None

    @abstractmethod
    def load(self):
        """Загружает конфигурацию игры"""
        pass

    @abstractmethod
    def save(self):
        """Сохраняет конфигурацию игры"""
        pass

    @abstractmethod
    def apply_preset(self, preset: Dict[str, Any]):
        """Применяет пресет настроек"""
        pass

    @abstractmethod
    def restore_backup(self) -> bool:
        """Восстанавливает последний бекап"""
        pass

    @staticmethod
    @abstractmethod
    def detect() -> Optional[Path]:
        """Автоматически определяет путь к игре"""
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Возвращает название игры"""
        pass