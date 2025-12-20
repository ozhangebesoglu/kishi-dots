# kishi_settings/pages/animations.py
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import re
import os


class AnimationsPage(Adw.PreferencesPage):
    # Debounce için timeout ID
    _save_timeout_id = None
    """Hyprland animasyon ayarları sayfası"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Animasyonlar")
        self.set_icon_name("preferences-desktop-effects-symbolic")

        self.config_path = os.path.expanduser("~/.config/hypr/animations.conf")
        self.animations = {}
        self.beziers = {}

        # Config'i oku
        self.load_config()

        # === Ana Kontroller ===
        main_group = Adw.PreferencesGroup(title="Ana Kontroller")
        self.add(main_group)

        # Animasyonları Aç/Kapat
        self.enabled_switch = Adw.SwitchRow(
            title="Animasyonları Etkinleştir",
            subtitle="Tüm animasyonları aç veya kapat"
        )
        self.enabled_switch.set_active(True)
        self.enabled_switch.connect("notify::active", self.on_enabled_changed)
        main_group.add(self.enabled_switch)

        # Global Hız
        global_speed_row = Adw.ActionRow()
        global_speed_row.set_title("Global Hız")
        global_speed_row.set_subtitle("Tüm animasyonların hız çarpanı (1-20)")

        self.global_speed_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 1, 20, 1
        )
        self.global_speed_scale.set_value(10)
        self.global_speed_scale.set_size_request(200, -1)
        self.global_speed_scale.set_valign(Gtk.Align.CENTER)
        self.global_speed_scale.connect("value-changed", self.on_global_speed_changed)
        global_speed_row.add_suffix(self.global_speed_scale)
        main_group.add(global_speed_row)

        # === Pencere Animasyonları ===
        window_group = Adw.PreferencesGroup(
            title="Pencere Animasyonları",
            description="Pencere açılma, kapanma ve hareket animasyonları"
        )
        self.add(window_group)

        # Windows genel
        self.windows_row = self.create_animation_row(
            "windows", "Pencere Genel", "Pencere hareketleri", 4.79
        )
        window_group.add(self.windows_row)

        # Windows In (açılma)
        self.windows_in_row = self.create_animation_row(
            "windowsIn", "Pencere Açılma", "Pencere açıldığında", 4.1,
            style_options=["popin", "slide", "fade"]
        )
        window_group.add(self.windows_in_row)

        # Windows Out (kapanma)
        self.windows_out_row = self.create_animation_row(
            "windowsOut", "Pencere Kapanma", "Pencere kapandığında", 1.49,
            style_options=["popin", "slide", "fade"]
        )
        window_group.add(self.windows_out_row)

        # === Fade Animasyonları ===
        fade_group = Adw.PreferencesGroup(
            title="Solma (Fade) Animasyonları",
            description="Öğelerin görünme ve kaybolma animasyonları"
        )
        self.add(fade_group)

        self.fade_in_row = self.create_animation_row(
            "fadeIn", "Görünme", "Öğeler görünürken", 1.73
        )
        fade_group.add(self.fade_in_row)

        self.fade_out_row = self.create_animation_row(
            "fadeOut", "Kaybolma", "Öğeler kaybolurken", 1.46
        )
        fade_group.add(self.fade_out_row)

        # === Workspace Animasyonları ===
        workspace_group = Adw.PreferencesGroup(
            title="Çalışma Alanı Animasyonları",
            description="Çalışma alanları arası geçiş animasyonları"
        )
        self.add(workspace_group)

        self.workspaces_row = self.create_animation_row(
            "workspaces", "Genel Geçiş", "Workspace değiştirirken", 1.94,
            style_options=["fade", "slide", "slidevert"]
        )
        workspace_group.add(self.workspaces_row)

        self.workspaces_in_row = self.create_animation_row(
            "workspacesIn", "Giriş", "Yeni workspace'e girerken", 1.21,
            style_options=["fade", "slide", "slidevert"]
        )
        workspace_group.add(self.workspaces_in_row)

        self.workspaces_out_row = self.create_animation_row(
            "workspacesOut", "Çıkış", "Eski workspace'ten çıkarken", 1.94,
            style_options=["fade", "slide", "slidevert"]
        )
        workspace_group.add(self.workspaces_out_row)

        # === Border ve Diğer ===
        other_group = Adw.PreferencesGroup(
            title="Diğer Animasyonlar",
            description="Border, katmanlar ve diğer efektler"
        )
        self.add(other_group)

        self.border_row = self.create_animation_row(
            "border", "Kenarlık", "Border renk değişimi", 5.39
        )
        other_group.add(self.border_row)

        self.layers_row = self.create_animation_row(
            "layers", "Katmanlar", "Overlay ve katmanlar", 3.81
        )
        other_group.add(self.layers_row)

        # === Bezier Eğrileri ===
        bezier_group = Adw.PreferencesGroup(
            title="Bezier Eğrileri",
            description="Animasyon hızlanma/yavaşlama eğrileri"
        )
        self.add(bezier_group)

        # Mevcut bezier'leri listele
        bezier_info = Adw.ActionRow()
        bezier_info.set_title("Tanımlı Eğriler")
        bezier_info.set_subtitle("easeOutQuint, easeInOutCubic, linear, almostLinear, quick")
        bezier_group.add(bezier_info)

        # Preset'ler
        preset_group = Adw.PreferencesGroup(title="Animasyon Preset'leri")
        self.add(preset_group)

        # Preset butonları
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        preset_box.set_halign(Gtk.Align.CENTER)
        preset_box.set_margin_top(10)
        preset_box.set_margin_bottom(10)

        smooth_btn = Gtk.Button(label="Yumuşak")
        smooth_btn.add_css_class("suggested-action")
        smooth_btn.connect("clicked", lambda b: self.apply_preset("smooth"))
        preset_box.append(smooth_btn)

        snappy_btn = Gtk.Button(label="Hızlı")
        snappy_btn.connect("clicked", lambda b: self.apply_preset("snappy"))
        preset_box.append(snappy_btn)

        minimal_btn = Gtk.Button(label="Minimal")
        minimal_btn.connect("clicked", lambda b: self.apply_preset("minimal"))
        preset_box.append(minimal_btn)

        none_btn = Gtk.Button(label="Kapalı")
        none_btn.add_css_class("destructive-action")
        none_btn.connect("clicked", lambda b: self.apply_preset("none"))
        preset_box.append(none_btn)

        preset_row = Adw.ActionRow()
        preset_row.set_title("Hızlı Ayarlar")
        preset_row.set_subtitle("Hazır animasyon profilleri")
        preset_row.set_child(preset_box)
        preset_group.add(preset_row)

    def create_animation_row(self, name, title, subtitle, default_speed, style_options=None):
        """Animasyon ayar satırı oluştur"""
        row = Adw.ExpanderRow()
        row.set_title(title)
        row.set_subtitle(subtitle)

        # Animasyon adını sakla
        row.animation_name = name

        # Etkinleştirme switch'i
        enable_switch = Gtk.Switch()
        enable_switch.set_active(True)
        enable_switch.set_valign(Gtk.Align.CENTER)
        enable_switch.connect("notify::active", self.on_animation_toggle, name)
        row.add_suffix(enable_switch)
        row.enable_switch = enable_switch

        # Hız ayarı
        speed_row = Adw.ActionRow()
        speed_row.set_title("Hız")

        speed_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.5, 10, 0.1
        )
        speed_scale.set_value(default_speed)
        speed_scale.set_size_request(200, -1)
        speed_scale.set_valign(Gtk.Align.CENTER)
        speed_scale.connect("value-changed", self.on_speed_changed, name)
        speed_row.add_suffix(speed_scale)
        row.add_row(speed_row)
        row.speed_scale = speed_scale

        # Bezier seçimi
        curve_row = Adw.ActionRow()
        curve_row.set_title("Eğri")

        curve_combo = Gtk.DropDown.new_from_strings([
            "easeOutQuint", "easeInOutCubic", "linear", "almostLinear", "quick"
        ])
        curve_combo.set_valign(Gtk.Align.CENTER)
        curve_combo.connect("notify::selected", self.on_curve_changed, name)
        curve_row.add_suffix(curve_combo)
        row.add_row(curve_row)
        row.curve_combo = curve_combo

        # Stil seçimi (varsa)
        if style_options:
            style_row = Adw.ActionRow()
            style_row.set_title("Stil")

            style_combo = Gtk.DropDown.new_from_strings(style_options)
            style_combo.set_valign(Gtk.Align.CENTER)
            style_combo.connect("notify::selected", self.on_style_changed, name)
            style_row.add_suffix(style_combo)
            row.add_row(style_row)
            row.style_combo = style_combo

        return row

    def load_config(self):
        """animations.conf dosyasını oku"""
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()

            # Bezier'leri parse et
            bezier_pattern = r'bezier\s*=\s*(\w+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)'
            for match in re.finditer(bezier_pattern, content):
                name = match.group(1)
                self.beziers[name] = [
                    float(match.group(2)), float(match.group(3)),
                    float(match.group(4)), float(match.group(5))
                ]

            # Animasyonları parse et
            anim_pattern = r'animation\s*=\s*(\w+),\s*(\d),\s*([\d.]+),\s*(\w+)(?:,\s*(.+))?'
            for match in re.finditer(anim_pattern, content):
                name = match.group(1)
                self.animations[name] = {
                    'enabled': match.group(2) == '1',
                    'speed': float(match.group(3)),
                    'curve': match.group(4),
                    'style': match.group(5).strip() if match.group(5) else None
                }

            print(f"Config yüklendi: {len(self.animations)} animasyon, {len(self.beziers)} bezier")

        except Exception as e:
            print(f"Config okuma hatası: {e}")

    def save_config(self):
        """animations.conf dosyasını kaydet (debounce ile)"""
        # Önceki timeout'u iptal et
        if self._save_timeout_id:
            GLib.source_remove(self._save_timeout_id)

        # 500ms sonra kaydet (debounce)
        self._save_timeout_id = GLib.timeout_add(500, self._do_save_config)

    def _do_save_config(self):
        """Gerçek kaydetme işlemi"""
        self._save_timeout_id = None

        try:
            # Mevcut içeriği oku
            with open(self.config_path, 'r') as f:
                content = f.read()

            # Her animasyonu güncelle
            for name, anim in self.animations.items():
                enabled = '1' if anim['enabled'] else '0'
                speed = anim['speed']
                curve = anim['curve']
                style = anim.get('style', '')

                # Regex ile satırı bul ve değiştir
                if style:
                    new_line = f"animation = {name},{' '*8 if len(name) < 8 else ' '}{enabled},     {speed:.2f},  {curve},       {style}"
                else:
                    new_line = f"animation = {name},{' '*8 if len(name) < 8 else ' '}{enabled},     {speed:.2f},  {curve}"

                pattern = rf'animation\s*=\s*{name},.*'
                content = re.sub(pattern, new_line.strip(), content)

            # Dosyaya yaz
            with open(self.config_path, 'w') as f:
                f.write(content)

            # Hyprland'ı yeniden yükle
            subprocess.run(['hyprctl', 'reload'], capture_output=True)

        except Exception as e:
            print(f"Config kaydetme hatası: {e}")

        return False  # Timeout'u tekrarlama

    def on_enabled_changed(self, switch, param):
        """Tüm animasyonları aç/kapat"""
        enabled = switch.get_active()
        print(f"Animasyonlar: {'Açık' if enabled else 'Kapalı'}")

        # Hyprctl ile değiştir
        value = "yes, please :)" if enabled else "no"
        subprocess.run([
            'hyprctl', 'keyword', 'animations:enabled', value
        ], capture_output=True)

    def on_global_speed_changed(self, scale):
        """Global hız değişti"""
        speed = scale.get_value()
        print(f"Global hız: {speed:.0f}")

        # Global animasyonu güncelle
        if 'global' in self.animations:
            self.animations['global']['speed'] = speed
            self.save_config()

    def on_animation_toggle(self, switch, param, name):
        """Tek bir animasyonu aç/kapat"""
        enabled = switch.get_active()
        print(f"{name} animasyonu: {'Açık' if enabled else 'Kapalı'}")

        if name in self.animations:
            self.animations[name]['enabled'] = enabled
            self.save_config()

    def on_speed_changed(self, scale, name):
        """Animasyon hızı değişti"""
        speed = scale.get_value()
        print(f"{name} hızı: {speed:.2f}")

        if name in self.animations:
            self.animations[name]['speed'] = speed
            self.save_config()

    def on_curve_changed(self, dropdown, param, name):
        """Bezier eğrisi değişti"""
        curves = ["easeOutQuint", "easeInOutCubic", "linear", "almostLinear", "quick"]
        selected = curves[dropdown.get_selected()]
        print(f"{name} eğrisi: {selected}")

        if name in self.animations:
            self.animations[name]['curve'] = selected
            self.save_config()

    def on_style_changed(self, dropdown, param, name):
        """Animasyon stili değişti"""
        model = dropdown.get_model()
        selected_idx = dropdown.get_selected()
        style = model.get_string(selected_idx)
        print(f"{name} stili: {style}")

        if name in self.animations:
            self.animations[name]['style'] = style
            self.save_config()

    def apply_preset(self, preset_name):
        """Animasyon preset'i uygula"""
        print(f"Preset uygulanıyor: {preset_name}")

        if preset_name == "smooth":
            # Yumuşak animasyonlar
            speeds = {
                'windows': 6.0, 'windowsIn': 5.0, 'windowsOut': 2.0,
                'fadeIn': 2.5, 'fadeOut': 2.0,
                'workspaces': 3.0, 'border': 6.0, 'layers': 4.0
            }
        elif preset_name == "snappy":
            # Hızlı animasyonlar
            speeds = {
                'windows': 2.0, 'windowsIn': 1.5, 'windowsOut': 0.8,
                'fadeIn': 1.0, 'fadeOut': 0.8,
                'workspaces': 1.0, 'border': 2.0, 'layers': 1.5
            }
        elif preset_name == "minimal":
            # Minimal animasyonlar
            speeds = {
                'windows': 3.0, 'windowsIn': 2.0, 'windowsOut': 1.0,
                'fadeIn': 1.5, 'fadeOut': 1.0,
                'workspaces': 1.5, 'border': 3.0, 'layers': 2.0
            }
        elif preset_name == "none":
            # Animasyonlar kapalı
            self.enabled_switch.set_active(False)
            return

        # Hızları uygula
        for name, speed in speeds.items():
            if name in self.animations:
                self.animations[name]['speed'] = speed

        self.save_config()

        # UI'ı güncelle
        self.show_toast(f"'{preset_name}' preset'i uygulandı!")

    def show_toast(self, message):
        """Toast mesajı göster"""
        toast = Adw.Toast.new(message)
        toast.set_timeout(2)

        # Window'u bul ve toast ekle
        window = self.get_root()
        if window and hasattr(window, 'add_toast'):
            window.add_toast(toast)
        else:
            print(message)
