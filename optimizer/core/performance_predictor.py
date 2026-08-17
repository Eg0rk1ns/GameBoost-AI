class PerformancePredictor:
    """Прогнозирует изменение FPS на основе настроек (коэффициенты — условные)"""
    
    base_fps = 120
    
    impact = {
        "gpu_mem_level": {"0": 1.25, "1": 1.0, "2": 0.85},
        "gpu_level": {"0": 1.35, "1": 1.1, "2": 0.95, "3": 0.8},
        "cl_globallight_shadow_mode": {"0": 1.15, "1": 1.0, "2": 0.9},
        "cl_particle_fallback_base": {"4": 1.2, "3": 1.05, "2": 1.0, "1": 0.95, "0": 0.9},
        "r_grass_quality": {"0": 1.15, "1": 1.05, "2": 1.0, "3": 0.95, "4": 0.9},
        "r_ssao": {"0": 1.08, "1": 0.95},
        "r_deferred_specular": {"0": 1.05, "1": 0.98},
        "r_deferred_specular_bloom": {"0": 1.05, "1": 0.98},
        "r_deferred_additive_pass": {"0": 1.05, "1": 0.98},
        "dota_cheap_water": {"0": 0.95, "1": 1.08},
        "r_deferred_height_fog": {"0": 1.05, "1": 0.98},
        "r_dota_fxaa": {"0": 1.05, "1": 0.98},
        "r_dota_normal_maps": {"0": 1.05, "1": 0.98},
        "dota_ambient_creatures": {"0": 1.05, "1": 0.98},
        "dota_ambient_cloth": {"0": 1.05, "1": 0.98},
        "r_dota_allow_wind_on_trees": {"0": 1.05, "1": 0.98},
        "r_depth_of_field": {"0": 1.08, "1": 0.96},
        "dota_portrait_animate": {"0": 1.05, "1": 0.98},
        "mat_vsync": {"0": 1.0, "1": 0.9},
    }
    
    @classmethod
    def predict_fps(cls, settings: dict, base_fps: int = None) -> int:
        if base_fps is None:
            base_fps = cls.base_fps
        multiplier = 1.0
        for cmd, value in settings.items():
            if cmd in cls.impact and value is not None:
                impact_dict = cls.impact[cmd]
                str_val = str(value)
                if str_val in impact_dict:
                    multiplier *= impact_dict[str_val]
        predicted = int(base_fps * multiplier)
        return max(10, min(500, predicted))
