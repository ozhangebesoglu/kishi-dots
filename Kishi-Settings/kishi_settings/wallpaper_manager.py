# kishi_settings/wallpaper_manager.py
import os
import json
import subprocess

class WallpaperManager:
    def __init__(self):
        self.waypaper_config = os.path.expanduser("~/.config/waypaper/config.ini")
        self.wallpaper_dir = self.get_wallpaper_directory()
        
    def get_wallpaper_directory(self):
        """Waypaper'ın kullandığı wallpaper dizinini al"""
        # Önce Türkçe dizini dene
        default_dir = os.path.expanduser("~/Resimler/Wallpapers")
        if os.path.exists(default_dir):
            return default_dir
        
        # Sonra İngilizce dizini
        default_dir = os.path.expanduser("~/Pictures/Wallpapers")
        if os.path.exists(default_dir):
            return default_dir
        
        # Config'den oku (varsa)
        if os.path.exists(self.waypaper_config):
            try:
                with open(self.waypaper_config, 'r') as f:
                    for line in f:
                        if 'folder' in line.lower():
                            path = line.split('=')[1].strip()
                            if os.path.exists(path):
                                return path
            except Exception as e:
                print(f"Config okuma hatası: {e}")
        
        # Hiçbiri yoksa Resimler klasörü
        return os.path.expanduser("~/Resimler")
    
    def get_current_wallpaper(self):
        """Şu anki wallpaper'ı al (swww'den)"""
        try:
            result = subprocess.run(
                ["swww", "query"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Output: "eDP-1: /path/to/wallpaper.png"
            for line in result.stdout.split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        return parts[1].strip()
        except Exception as e:
            print(f"Wallpaper query hatası: {e}")
        return None
    
    def get_wallpaper_list(self):
        """Tüm wallpaper'ları listele"""
        wallpapers = []
        extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')
        
        print(f"📁 Wallpaper dizini aranıyor: {self.wallpaper_dir}")
        
        if not os.path.exists(self.wallpaper_dir):
            print(f"❌ Dizin bulunamadı: {self.wallpaper_dir}")
            return wallpapers
        
        try:
            files = os.listdir(self.wallpaper_dir)
            print(f"📂 Toplam {len(files)} dosya bulundu")
            
            for file in files:
                if file.lower().endswith(extensions):
                    full_path = os.path.join(self.wallpaper_dir, file)
                    wallpapers.append({
                        'name': file,
                        'path': full_path,
                        'size': os.path.getsize(full_path)
                    })
            
            print(f"🖼️  {len(wallpapers)} wallpaper bulundu")
            
        except Exception as e:
            print(f"❌ Dizin okuma hatası: {e}")
        
        return sorted(wallpapers, key=lambda x: x['name'])
    
    def set_wallpaper(self, image_path, transition="fade", duration=2):
        """Wallpaper'ı değiştir (swww ile)"""
        try:
            subprocess.run([
                "swww", "img", image_path,
                "--transition-type", transition,
                "--transition-duration", str(duration)
            ], timeout=10)
            return True
        except Exception as e:
            print(f"Wallpaper değiştirme hatası: {e}")
            return False