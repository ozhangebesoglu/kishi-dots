# kishi_settings/wallpaper_cache.py
import os
import json
import hashlib
from gi.repository import GdkPixbuf, Gdk

class WallpaperCache:
    def __init__(self):
        self.cache_dir = os.path.expanduser("~/.cache/kishi-settings/wallpapers")
        self.cache_index = os.path.join(self.cache_dir, "index.json")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache index'i yükle
        self.index = self.load_index()
    
    def load_index(self):
        """Cache index'ini yükle"""
        if os.path.exists(self.cache_index):
            try:
                with open(self.cache_index, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_index(self):
        """Cache index'ini kaydet"""
        try:
            with open(self.cache_index, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Cache index kaydetme hatası: {e}")
    
    def get_cache_path(self, wallpaper_path):
        """Wallpaper için cache dosya yolu"""
        # Hash ile unique dosya adı oluştur
        file_hash = hashlib.md5(wallpaper_path.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{file_hash}.png")
    
    def is_cached(self, wallpaper_path):
        """Wallpaper cache'de var mı?"""
        cache_path = self.get_cache_path(wallpaper_path)
        
        # Cache dosyası var mı ve güncel mi?
        if os.path.exists(cache_path):
            # Orijinal dosya değişti mi kontrol et
            if wallpaper_path in self.index:
                cached_mtime = self.index[wallpaper_path].get('mtime', 0)
                current_mtime = os.path.getmtime(wallpaper_path)
                
                if cached_mtime >= current_mtime:
                    return True
        
        return False
    
    def get_thumbnail(self, wallpaper_path):
        """Cache'den thumbnail al"""
        if self.is_cached(wallpaper_path):
            cache_path = self.get_cache_path(wallpaper_path)
            try:
                return GdkPixbuf.Pixbuf.new_from_file(cache_path)
            except:
                pass
        return None
    
    def create_thumbnail(self, wallpaper_path, width=200, height=150):
        """Thumbnail oluştur ve cache'le"""
        try:
            # Thumbnail oluştur
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                wallpaper_path,
                width,
                height,
                False
            )
            
            # Cache'e kaydet
            cache_path = self.get_cache_path(wallpaper_path)
            pixbuf.savev(cache_path, "png", [], [])
            
            # Index'e ekle
            self.index[wallpaper_path] = {
                'mtime': os.path.getmtime(wallpaper_path),
                'cache_path': cache_path
            }
            self.save_index()
            
            return pixbuf
            
        except Exception as e:
            print(f"Thumbnail oluşturma hatası ({wallpaper_path}): {e}")
            return None
    
    def clear_cache(self):
        """Cache'i temizle"""
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
        self.index = {}
        self.save_index()