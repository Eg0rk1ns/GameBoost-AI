from optimizer.utils.paths import find_dota2_path
from optimizer.core.profile_applier import Dota2Config

def main():
    dota_path = find_dota2_path()
    if dota_path is None:
        print("Dota 2 не найдена. Укажите путь вручную.")
        return

    print(f"Найден путь: {dota_path}")

    performance_preset = {
        "setting.gpu_mem_level": "0",
        "setting.graphics_quality": "0",
        "setting.shadow_quality": "0",
        "setting.vsync": "0",
        "setting.fps_max": "0"
    }

    try:
        config = Dota2Config(dota_path)
        config.load()
        config.apply_preset(performance_preset)
        print("Настройки успешно применены!")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()