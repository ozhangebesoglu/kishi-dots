# kishi_settings/config.py
import os
import json

class KishiConfig:
    """Kishi Settings konfigürasyon yönetimi"""
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/kishi-settings")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "light_mode": False,
            "auto_apply_theme": True,
            "last_wallpaper": "",
            "theme_apps": {
                "hyprland": True,
                "waybar": True,
                "rofi": True,
                "kitty": True,
                "wlogout": True,
                "swaync": True,
                "hyprlock": True,
                "fastfetch": True,
                "gtk": True,
                "powermenu": True
            }
        }
        self._ensure_config_dir()
        self.config = self._load_config()
    
    def _ensure_config_dir(self):
        """Config dizinini oluştur"""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _load_config(self):
        """Config dosyasını yükle"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Eksik anahtarları default ile doldur
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Config yükleme hatası: {e}")
        return self.default_config.copy()
    
    def save(self):
        """Config'i kaydet"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Config kaydetme hatası: {e}")
    
    @property
    def light_mode(self):
        return self.config.get("light_mode", False)
    
    @light_mode.setter
    def light_mode(self, value):
        self.config["light_mode"] = value
        self.save()
    
    @property
    def auto_apply_theme(self):
        return self.config.get("auto_apply_theme", True)
    
    @auto_apply_theme.setter
    def auto_apply_theme(self, value):
        self.config["auto_apply_theme"] = value
        self.save()
    
    @property
    def last_wallpaper(self):
        return self.config.get("last_wallpaper", "")
    
    @last_wallpaper.setter
    def last_wallpaper(self, value):
        self.config["last_wallpaper"] = value
        self.save()
