# kishi_settings/color_extractor.py - İYİLEŞTİRİLMİŞ VERSİYON
from PIL import Image
import colorsys
from sklearn.cluster import KMeans
import numpy as np

class WallpaperColorExtractor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        
        # RGBA ise RGB'ye çevir (PNG dosyaları için)
        if self.image.mode == 'RGBA':
            self.image = self.image.convert('RGB')
        elif self.image.mode != 'RGB':
            self.image = self.image.convert('RGB')
        
    def get_dominant_colors(self, n_colors=16):
        """K-means ile dominant renkleri çıkar - daha fazla renk"""
        # Resmi küçült (performans için)
        img = self.image.resize((200, 200))
        img_array = np.array(img)
        
        # RGB olduğundan emin ol (3 kanal)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]
        
        # RGB pixel'leri düzleştir
        pixels = img_array.reshape(-1, 3)
        
        # Çok koyu (<20) ve çok açık (>235) renkleri filtrele
        brightness = 0.299 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.114 * pixels[:, 2]
        mask = (brightness > 20) & (brightness < 235)
        filtered_pixels = pixels[mask]
        
        if len(filtered_pixels) < 100:
            filtered_pixels = pixels  # Yeterli renk yoksa tümünü kullan
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(filtered_pixels)
        
        # Renkleri sırala (brightness'a göre)
        colors = kmeans.cluster_centers_.astype(int)
        colors_with_brightness = [
            (color, self._get_brightness(color)) 
            for color in colors
        ]
        colors_with_brightness.sort(key=lambda x: x[1])
        
        return [color for color, _ in colors_with_brightness]
    
    def _get_brightness(self, rgb):
        """Rengin brightness'ını hesapla"""
        return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    
    def _get_saturation(self, rgb):
        """Rengin saturation'ını hesapla"""
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        return s
    
    def generate_gruvbox_palette(self):
        """Wallpaper'dan Gruvbox benzeri palet oluştur - İYİLEŞTİRİLMİŞ"""
        dominant_colors = self.get_dominant_colors(n_colors=20)  # Daha fazla renk
        
        # Saturation'a göre renkli olanları ayır
        colorful = [c for c in dominant_colors if self._get_saturation(c) > 0.2]
        neutral = [c for c in dominant_colors if self._get_saturation(c) <= 0.2]
        
        # Hue kategorilerine ayır
        hue_colors = {
            'red': [],
            'orange': [],
            'yellow': [],
            'green': [],
            'aqua': [],
            'blue': [],
            'purple': []
        }
        
        for color in colorful:
            h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
            hue = h * 360
            
            # Hue'ya göre kategorize et
            if 345 <= hue or hue < 15:
                hue_colors['red'].append(color)
            elif 15 <= hue < 45:
                hue_colors['orange'].append(color)
            elif 45 <= hue < 75:
                hue_colors['yellow'].append(color)
            elif 75 <= hue < 165:
                hue_colors['green'].append(color)
            elif 165 <= hue < 195:
                hue_colors['aqua'].append(color)
            elif 195 <= hue < 255:
                hue_colors['blue'].append(color)
            elif 255 <= hue < 345:
                hue_colors['purple'].append(color)
        
        # En koyu ve en açık nötr renkleri bul
        if neutral:
            bg = min(neutral, key=lambda c: self._get_brightness(c))
            fg = max(neutral, key=lambda c: self._get_brightness(c))
        else:
            bg = min(dominant_colors, key=lambda c: self._get_brightness(c))
            fg = max(dominant_colors, key=lambda c: self._get_brightness(c))
        
        # Palette oluştur
        palette = {
            'bg': bg,
            'bg0': self._adjust_brightness(bg, 0.9),
            'bg1': self._adjust_brightness(bg, 1.15),
            'bg2': self._adjust_brightness(bg, 1.3),
            'fg': fg,
        }
        
        # Her hue kategorisi için en iyi rengi seç
        for hue_name, colors in hue_colors.items():
            if colors:
                # En canlı ve orta parlaklıktaki rengi seç
                best = max(colors, key=lambda c: self._get_saturation(c))
                # Rengi biraz daha canlı yap
                palette[hue_name] = self._enhance_color(best)
            else:
                # Eğer o renk yoksa, en yakın hue'dan sentetik oluştur
                palette[hue_name] = self._generate_color_for_hue(
                    self._hue_name_to_degree(hue_name),
                    dominant_colors
                )
        
        return palette
    
    def _hue_name_to_degree(self, name):
        """Hue ismini derece'ye çevir"""
        hue_map = {
            'red': 0,
            'orange': 30,
            'yellow': 60,
            'green': 120,
            'aqua': 180,
            'blue': 240,
            'purple': 300
        }
        return hue_map.get(name, 0)
    
    def _generate_color_for_hue(self, target_hue, base_colors):
        """Belirli bir hue için renk oluştur"""
        # En canlı rengi bul
        best_base = max(base_colors, key=lambda c: self._get_saturation(c))
        h, s, v = colorsys.rgb_to_hsv(best_base[0]/255, best_base[1]/255, best_base[2]/255)
        
        # Hue'yu değiştir, saturation ve value'yu koru
        h = target_hue / 360
        s = max(0.6, s)  # En az %60 saturation
        v = max(0.5, min(0.8, v))  # Orta parlaklık
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _enhance_color(self, color):
        """Rengi daha canlı yap"""
        h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        
        # Saturation'ı artır
        s = min(1.0, s * 1.4)
        
        # Value'yu optimize et (çok koyu veya açık olmasın)
        if v < 0.4:
            v = min(0.6, v * 1.5)
        elif v > 0.9:
            v = 0.85
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _adjust_brightness(self, color, factor):
        """Rengin parlaklığını ayarla"""
        h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        v = min(1.0, v * factor)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def rgb_to_hex(self, rgb):
        """RGB'yi hex'e çevir"""
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    def export_palette(self, light_mode=False):
        """Paleti export et - Dark veya Light mode"""
        palette = self.generate_gruvbox_palette()
        
        if light_mode:
            palette = self._convert_to_light_mode(palette)
        
        return {key: self.rgb_to_hex(value) for key, value in palette.items()}
    
    def _convert_to_light_mode(self, palette):
        """Dark mode paletini light mode'a çevir - wallpaper rengine uygun"""
        light_palette = {}
        
        # Wallpaper'ın dominant accent rengini bul
        accent_colors = ['red', 'orange', 'yellow', 'green', 'aqua', 'blue', 'purple']
        dominant_accent = None
        max_saturation = 0
        
        for color_name in accent_colors:
            if color_name in palette:
                color = palette[color_name]
                h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
                if s > max_saturation:
                    max_saturation = s
                    dominant_accent = palette[color_name]
        
        # Eğer dominant accent bulunamadıysa, palette'ten en canlı rengi al
        if dominant_accent is None:
            dominant_accent = palette.get('blue', [100, 150, 200])
        
        # Background: Dominant rengin çok açık tonu
        # Örn: Kırmızı wallpaper -> açık pembe bg
        light_palette['bg'] = self._create_tinted_light_bg(dominant_accent, 0.97)  # Çok açık
        light_palette['bg0'] = self._create_tinted_light_bg(dominant_accent, 0.95)
        light_palette['bg1'] = self._create_tinted_light_bg(dominant_accent, 0.92)
        light_palette['bg2'] = self._create_tinted_light_bg(dominant_accent, 0.88)
        
        # Foreground: Dominant rengin koyu tonu
        light_palette['fg'] = self._create_dark_fg_from_accent(dominant_accent)
        
        # Accent renkleri - light mode için ayarla
        for color_name in accent_colors:
            if color_name in palette:
                light_palette[color_name] = self._adjust_for_light_bg(palette[color_name])
        
        # Gray - dominant renge uygun gri
        light_palette['gray'] = self._create_tinted_gray(dominant_accent)
        
        return light_palette
    
    def _create_tinted_light_bg(self, accent_color, lightness):
        """Accent renginin çok açık, hafif renkli versiyonu"""
        h, s, v = colorsys.rgb_to_hsv(accent_color[0]/255, accent_color[1]/255, accent_color[2]/255)
        
        # Hue'yu koru, saturation'ı çok düşür, value'yu çok yükselt
        s = s * 0.08  # Çok az renk tonu (hafif kırmızımsı, mavimsi vs.)
        v = lightness  # Çok açık (0.95-0.97)
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _create_dark_fg_from_accent(self, accent_color):
        """Accent renginin koyu versiyonu - foreground için"""
        h, s, v = colorsys.rgb_to_hsv(accent_color[0]/255, accent_color[1]/255, accent_color[2]/255)
        
        # Hue'yu koru, saturation'ı biraz koru, value'yu düşür
        s = s * 0.3  # Biraz renk tonu
        v = 0.25  # Koyu
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _create_tinted_gray(self, accent_color):
        """Accent rengine uygun gri"""
        h, s, v = colorsys.rgb_to_hsv(accent_color[0]/255, accent_color[1]/255, accent_color[2]/255)
        
        s = s * 0.15  # Hafif renk tonu
        v = 0.45  # Orta gri
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _adjust_for_light_bg(self, color):
        """Rengi açık arka plan için ayarla - daha koyu ve canlı"""
        h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        
        # Saturation'ı artır (daha canlı)
        s = min(1.0, s * 1.3)
        
        # Value'yu düşür (açık bg'de koyu renkler daha iyi okunur)
        v = min(0.7, v * 0.75)
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _lighten_color(self, color, target_value):
        """Rengi açıklaştır - value'yu artır"""
        h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        # Saturation'ı düşür, value'yu yükselt
        s = s * 0.3  # Light mode'da az saturation
        v = target_value
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _darken_color(self, color, factor):
        """Rengi koyulaştır - value'yu düşür"""
        h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        # Saturation'ı artır, value'yu düşür
        s = min(1.0, s * 1.2)
        v = v * factor
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 255), int(g * 255), int(b * 255)]