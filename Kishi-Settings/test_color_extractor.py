# test_color_extractor.py
from kishi_settings.color_extractor import WallpaperColorExtractor

# Bir wallpaper seç (kendi yolunu yaz)
wallpaper_path = "/home/ozhan/Resimler/Wallpapers/anime-girl-katana-tattoo-4k-wallpaper-uhdpaper.com-639@5@f.jpg"

extractor = WallpaperColorExtractor(wallpaper_path)
palette = extractor.export_palette()

print("🎨 Extracted Colors:")
for name, color in palette.items():
    print(f"  {name}: {color}")