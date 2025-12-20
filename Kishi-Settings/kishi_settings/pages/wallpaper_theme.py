# kishi_settings/pages/wallpaper_theme.py
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GdkPixbuf, Gio, Gdk, GLib
import os
import threading

from kishi_settings.wallpaper_manager import WallpaperManager
from kishi_settings.wallpaper_cache import WallpaperCache
from kishi_settings.color_extractor import WallpaperColorExtractor
from kishi_settings.theme_generator import ThemeGenerator
from kishi_settings.config import KishiConfig


class WallpaperThemePage(Adw.PreferencesPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Duvar Kağıdı Temaları")
        self.set_icon_name("preferences-desktop-wallpaper-symbolic")

        self.wallpaper_manager = WallpaperManager()
        self.wallpaper_cache = WallpaperCache()
        self.kishi_config = KishiConfig()  # Config yönetimi
        self.selected_wallpaper = None
        self.loading = False
        self.loaded_count = 0
        self.extracted_palette = None
        
        # Config'den light mode durumunu al
        self.light_mode = self.kishi_config.light_mode
        
        # Uygulama başladığında cache'i temizle (wallpaperların taze yüklenmesi için)
        self.wallpaper_cache.clear_cache()

        print(f"\n{'='*60}")
        print(f"Wallpaper Manager başlatıldı")
        print(f"Wallpaper dizini: {self.wallpaper_manager.wallpaper_dir}")
        print(f"Cache dizini: {self.wallpaper_cache.cache_dir}")
        print(f"Light Mode: {self.light_mode}")
        print(f"Cache otomatik temizlendi")
        print(f"{'='*60}\n")

        # === Mevcut Wallpaper ===
        current_group = Adw.PreferencesGroup(title="Şu Anki Duvar Kağıdı")
        self.add(current_group)

        self.current_wallpaper_row = Adw.ActionRow()
        self.current_wallpaper_row.set_title("Yükleniyor...")
        current_group.add(self.current_wallpaper_row)

        # Mevcut wallpaper'ı yükle
        self.load_current_wallpaper()

        # === Wallpaper Galerisi ===
        gallery_group = Adw.PreferencesGroup(
            title="Wallpaper Galerisi",
            description="Bir wallpaper seçin ve otomatik tema oluşturun"
        )
        self.add(gallery_group)

        # Scroll container
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)
        scrolled.set_max_content_height(500)

        # FlowBox (grid layout)
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(4)
        self.flowbox.set_min_children_per_line(2)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_row_spacing(10)
        self.flowbox.set_column_spacing(10)
        self.flowbox.connect("child-activated", self.on_wallpaper_selected)

        scrolled.set_child(self.flowbox)

        # Loading indicator
        self.loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.loading_box.set_valign(Gtk.Align.CENTER)
        self.loading_box.set_margin_top(50)
        self.loading_box.set_margin_bottom(50)

        self.loading_spinner = Gtk.Spinner()
        self.loading_spinner.set_size_request(48, 48)
        self.loading_spinner.start()

        self.loading_label = Gtk.Label(label="Wallpaper'lar yükleniyor...")
        self.loading_label.add_css_class("title-2")

        self.loading_progress = Gtk.Label(label="0 / 0")
        self.loading_progress.add_css_class("dim-label")

        self.loading_box.append(self.loading_spinner)
        self.loading_box.append(self.loading_label)
        self.loading_box.append(self.loading_progress)

        self.flowbox.append(self.loading_box)

        # Gallery'yi bir expander içine koy
        expander = Adw.ExpanderRow()
        expander.set_title("Wallpaper'ları Göster")
        expander.set_subtitle(f"{self.wallpaper_manager.wallpaper_dir}")
        expander.add_row(scrolled)
        expander.connect("notify::enable-expansion", self.on_expander_toggled)
        gallery_group.add(expander)

        self.expander = expander

        # Wallpaper listesi (henüz yüklenmesin)
        self.wallpapers = []

        # === Renk Önizlemesi ===
        self.color_preview_group = Adw.PreferencesGroup(title="Çıkarılan Renkler")
        self.add(self.color_preview_group)

        # Renk kutucukları için container
        self.color_preview_row = Adw.ActionRow()
        self.color_preview_row.set_title("Wallpaper seçilmedi")
        self.color_preview_row.set_subtitle("Bir wallpaper seçerek renk paletini görün")

        self.color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.color_box.set_valign(Gtk.Align.CENTER)
        self.color_preview_row.add_suffix(self.color_box)

        self.color_preview_group.add(self.color_preview_row)

        # === Tema Ayarları ===
        theme_group = Adw.PreferencesGroup(title="Tema Oluşturma Ayarları")
        self.add(theme_group)

        # Dark / Light Mode Switch
        self.dark_light_row = Adw.ActionRow()
        self.dark_light_row.set_title("Tema Modu")
        self.dark_light_row.set_subtitle("Dark veya Light mode seç (Waypaper'da da geçerli)")

        # SegmentedButton ile Dark/Light seçimi
        self.mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.mode_box.add_css_class("linked")
        self.mode_box.set_valign(Gtk.Align.CENTER)

        self.dark_btn = Gtk.ToggleButton(label="🌙 Dark")
        self.light_btn = Gtk.ToggleButton(label="☀️ Light")

        # Config'den başlangıç durumunu al
        if self.light_mode:
            self.light_btn.set_active(True)
            self.dark_btn.set_active(False)
        else:
            self.dark_btn.set_active(True)
            self.light_btn.set_active(False)

        self.dark_btn.connect("toggled", self.on_dark_mode_toggled)
        self.light_btn.connect("toggled", self.on_light_mode_toggled)

        self.mode_box.append(self.dark_btn)
        self.mode_box.append(self.light_btn)

        self.dark_light_row.add_suffix(self.mode_box)
        theme_group.add(self.dark_light_row)

        # Canlılık (Saturation) slider
        self.saturation_row = Adw.ActionRow()
        self.saturation_row.set_title("Renk Canlılığı")
        self.saturation_row.set_subtitle("Renklerin ne kadar canlı olacağı")

        self.saturation_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.5, 1.5, 0.1
        )
        self.saturation_scale.set_value(1.0)
        self.saturation_scale.set_size_request(200, -1)
        self.saturation_scale.set_valign(Gtk.Align.CENTER)
        self.saturation_scale.connect("value-changed", self.on_saturation_changed)
        self.saturation_row.add_suffix(self.saturation_scale)
        theme_group.add(self.saturation_row)

        # Parlaklık (Brightness) slider
        self.brightness_row = Adw.ActionRow()
        self.brightness_row.set_title("Parlaklık")
        self.brightness_row.set_subtitle("Arka plan renklerinin parlaklığı")

        self.brightness_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.5, 1.5, 0.1
        )
        self.brightness_scale.set_value(1.0)
        self.brightness_scale.set_size_request(200, -1)
        self.brightness_scale.set_valign(Gtk.Align.CENTER)
        self.brightness_scale.connect("value-changed", self.on_brightness_changed)
        self.brightness_row.add_suffix(self.brightness_scale)
        theme_group.add(self.brightness_row)

        # === Uygulama Seçenekleri ===
        apply_group = Adw.PreferencesGroup(title="Temayı Uygula")
        self.add(apply_group)

        self.hyprland_switch = Adw.SwitchRow(title="Hyprland Renkleri")
        self.hyprland_switch.set_subtitle("Border ve gölge renkleri")
        self.hyprland_switch.set_active(True)
        apply_group.add(self.hyprland_switch)

        self.waybar_switch = Adw.SwitchRow(title="Waybar Teması")
        self.waybar_switch.set_subtitle("Üst bar renkleri")
        self.waybar_switch.set_active(True)
        apply_group.add(self.waybar_switch)

        self.rofi_switch = Adw.SwitchRow(title="Rofi Teması")
        self.rofi_switch.set_subtitle("Uygulama launcher renkleri")
        self.rofi_switch.set_active(True)
        apply_group.add(self.rofi_switch)

        self.kitty_switch = Adw.SwitchRow(title="Kitty Terminal")
        self.kitty_switch.set_subtitle("Terminal renkleri")
        self.kitty_switch.set_active(True)
        apply_group.add(self.kitty_switch)

        self.change_wallpaper_switch = Adw.SwitchRow(
            title="Duvar Kağıdını Değiştir",
            subtitle="Temayı uygularken wallpaper'ı da değiştir"
        )
        self.change_wallpaper_switch.set_active(True)
        apply_group.add(self.change_wallpaper_switch)

        # Uygula butonu
        apply_row = Adw.ActionRow()
        apply_row.set_title("Seçili Wallpaper'dan Tema Oluştur")

        self.apply_btn = Gtk.Button(label="Tema Oluştur ve Uygula")
        self.apply_btn.add_css_class("suggested-action")
        self.apply_btn.set_valign(Gtk.Align.CENTER)
        self.apply_btn.connect("clicked", self.on_create_theme)
        self.apply_btn.set_sensitive(False)
        apply_row.add_suffix(self.apply_btn)
        apply_group.add(apply_row)

        # === Cache Yönetimi ===
        cache_group = Adw.PreferencesGroup(title="Cache Yönetimi")
        self.add(cache_group)

        cache_row = Adw.ActionRow()
        cache_row.set_title("Önbelleği Temizle")
        cache_row.set_subtitle("Wallpaper thumbnail'larını yeniden oluştur")

        clear_cache_btn = Gtk.Button(label="Temizle")
        clear_cache_btn.set_valign(Gtk.Align.CENTER)
        clear_cache_btn.connect("clicked", self.on_clear_cache)
        cache_row.add_suffix(clear_cache_btn)
        cache_group.add(cache_row)

        # === Waypaper Butonu ===
        waypaper_group = Adw.PreferencesGroup(title="Gelişmiş")
        self.add(waypaper_group)

        waypaper_row = Adw.ActionRow()
        waypaper_row.set_title("Waypaper'ı Aç")
        waypaper_row.set_subtitle("Tam özellikli wallpaper yöneticisi")

        waypaper_btn = Gtk.Button(label="Aç")
        waypaper_btn.set_valign(Gtk.Align.CENTER)
        waypaper_btn.connect("clicked", self.open_waypaper)
        waypaper_row.add_suffix(waypaper_btn)
        waypaper_group.add(waypaper_row)

    def on_expander_toggled(self, expander, param):
        """Expander açıldığında wallpaper'ları yükle"""
        if expander.get_enable_expansion() and not self.loading and not self.wallpapers:
            self.load_wallpapers_async()

    def load_current_wallpaper(self):
        """Mevcut wallpaper'ı göster"""
        current = self.wallpaper_manager.get_current_wallpaper()
        if current:
            name = os.path.basename(current)
            self.current_wallpaper_row.set_title(name)
            self.current_wallpaper_row.set_subtitle(current)

            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(current, 48, 48, True)
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                image = Gtk.Image.new_from_paintable(texture)
                self.current_wallpaper_row.add_prefix(image)
            except Exception as e:
                print(f"Thumbnail yükleme hatası: {e}")

    def load_wallpapers_async(self):
        """Wallpaper'ları asenkron olarak yükle"""
        if self.loading:
            return

        self.loading = True
        self.loaded_count = 0

        self.wallpapers = self.wallpaper_manager.get_wallpaper_list()

        print(f"\n{len(self.wallpapers)} wallpaper asenkron yükleniyor...")

        GLib.idle_add(self.loading_label.set_text, f"{len(self.wallpapers)} wallpaper yükleniyor...")
        GLib.idle_add(self.loading_progress.set_text, f"0 / {len(self.wallpapers)}")

        thread = threading.Thread(target=self._load_wallpapers_thread, daemon=True)
        thread.start()

    def _load_wallpapers_thread(self):
        """Arka plan thread'de wallpaper'ları yükle"""
        for i, wallpaper in enumerate(self.wallpapers):
            pixbuf = self.wallpaper_cache.get_thumbnail(wallpaper['path'])

            if pixbuf is None:
                pixbuf = self.wallpaper_cache.create_thumbnail(wallpaper['path'], 200, 150)

            if pixbuf:
                GLib.idle_add(self._add_wallpaper_widget, wallpaper, pixbuf)

            self.loaded_count = i + 1
            GLib.idle_add(self.loading_progress.set_text, f"{self.loaded_count} / {len(self.wallpapers)}")

            if i > 50 and i % 10 == 0:
                import time
                time.sleep(0.01)

        GLib.idle_add(self._loading_complete)

    def _add_wallpaper_widget(self, wallpaper, pixbuf):
        """UI thread'de wallpaper widget'ı ekle"""
        try:
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            picture = Gtk.Picture.new_for_paintable(texture)
            picture.set_content_fit(Gtk.ContentFit.COVER)
            picture.set_size_request(200, 150)

            overlay = Gtk.Overlay()
            overlay.set_child(picture)
            overlay.wallpaper_path = wallpaper['path']

            label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            label_box.set_valign(Gtk.Align.END)

            label = Gtk.Label(label=wallpaper['name'])
            label.add_css_class("caption")
            label.set_ellipsize(3)
            label.set_max_width_chars(25)
            label.set_margin_start(5)
            label.set_margin_end(5)
            label.set_margin_bottom(5)

            label_bg = Gtk.Box()
            label_bg.append(label)
            label_bg.add_css_class("card")
            label_bg.set_opacity(0.9)

            label_box.append(label_bg)
            overlay.add_overlay(label_box)

            self.flowbox.append(overlay)

        except Exception as e:
            print(f"Widget oluşturma hatası: {e}")

    def _loading_complete(self):
        """Yükleme tamamlandı"""
        self.flowbox.remove(self.loading_box)
        self.loading = False
        print(f"{self.loaded_count} wallpaper yüklendi!\n")

    def on_clear_cache(self, button):
        """Cache'i temizle"""
        self.wallpaper_cache.clear_cache()

        child = self.flowbox.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.flowbox.remove(child)
            child = next_child

        self.flowbox.append(self.loading_box)
        self.wallpapers = []
        self.loaded_count = 0

        if self.expander.get_enable_expansion():
            self.load_wallpapers_async()

        print("Cache temizlendi")

    def on_wallpaper_selected(self, flowbox, child):
        """Wallpaper seçildiğinde"""
        try:
            overlay = child.get_child()

            if hasattr(overlay, 'wallpaper_path') and overlay.wallpaper_path:
                self.selected_wallpaper = overlay.wallpaper_path
                self.apply_btn.set_sensitive(True)

                name = os.path.basename(self.selected_wallpaper)
                short_name = name[:30] + '...' if len(name) > 30 else name
                self.apply_btn.set_label(f"'{short_name}' için Tema Oluştur")

                print(f"Wallpaper seçildi: {name}")

                # Renkleri çıkar ve önizle
                self.extract_and_preview_colors()
            else:
                print("Geçerli bir wallpaper seçilmedi")
                self.apply_btn.set_sensitive(False)
                self.apply_btn.set_label("Tema Oluştur ve Uygula")

        except Exception as e:
            print(f"Wallpaper seçim hatası: {e}")
            self.apply_btn.set_sensitive(False)

    def extract_and_preview_colors(self):
        """Seçili wallpaper'dan renkleri çıkar ve önizle"""
        if not self.selected_wallpaper:
            return

        try:
            # Renk çıkarıcıyı başlat
            extractor = WallpaperColorExtractor(self.selected_wallpaper)
            self.extracted_palette = extractor.export_palette(light_mode=self.light_mode)

            # Önizleme satırını güncelle
            name = os.path.basename(self.selected_wallpaper)
            mode_text = "Light" if self.light_mode else "Dark"
            self.color_preview_row.set_title(f"Renkler: {name} ({mode_text})")
            self.color_preview_row.set_subtitle("Wallpaper'dan çıkarılan Gruvbox paleti")

            # Eski renk kutucuklarını temizle
            child = self.color_box.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self.color_box.remove(child)
                child = next_child

            # Yeni renk kutucukları ekle
            color_order = ['bg', 'bg1', 'fg', 'red', 'orange', 'yellow', 'green', 'aqua', 'blue', 'purple']

            for color_name in color_order:
                if color_name in self.extracted_palette:
                    hex_color = self.extracted_palette[color_name]
                    color_widget = self.create_color_box(hex_color, color_name)
                    self.color_box.append(color_widget)

            print(f"Renkler çıkarıldı: {self.extracted_palette}")

        except Exception as e:
            print(f"Renk çıkarma hatası: {e}")
            self.color_preview_row.set_title("Renk çıkarma hatası")
            self.color_preview_row.set_subtitle(str(e))

    def create_color_box(self, hex_color, name):
        """Renk önizleme kutusu oluştur"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_valign(Gtk.Align.CENTER)

        # Renk kutusu
        color_area = Gtk.DrawingArea()
        color_area.set_size_request(28, 28)
        color_area.set_content_width(28)
        color_area.set_content_height(28)

        # CSS ile renk ayarla
        css_provider = Gtk.CssProvider()
        css = f"""
            drawingarea {{
                background-color: {hex_color};
                border-radius: 4px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
        """
        css_provider.load_from_data(css.encode())
        color_area.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Tooltip
        box.set_tooltip_text(f"{name}: {hex_color}")

        box.append(color_area)
        return box

    def on_dark_mode_toggled(self, button):
        """Dark mode seçildiğinde"""
        if button.get_active():
            self.light_mode = False
            self.kishi_config.light_mode = False  # Config'e kaydet
            self.light_btn.set_active(False)
            print("Dark mode seçildi ve kaydedildi")
            
            # Uygulamanın kendi temasını değiştir
            self._update_app_color_scheme()
            
            # Renkleri yeniden çıkar
            if self.selected_wallpaper:
                self.extract_colors()

    def on_light_mode_toggled(self, button):
        """Light mode seçildiğinde"""
        if button.get_active():
            self.light_mode = True
            self.kishi_config.light_mode = True  # Config'e kaydet
            self.dark_btn.set_active(False)
            print("Light mode seçildi ve kaydedildi")
            
            # Uygulamanın kendi temasını değiştir
            self._update_app_color_scheme()
            
            # Renkleri yeniden çıkar
            if self.selected_wallpaper:
                self.extract_colors()
    
    def _update_app_color_scheme(self):
        """Kishi Settings uygulamasının color scheme'ini güncelle"""
        try:
            style_manager = Adw.StyleManager.get_default()
            if self.light_mode:
                style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
            else:
                style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        except Exception as e:
            print(f"Color scheme güncelleme hatası: {e}")

    def on_saturation_changed(self, scale):
        """Canlılık değiştiğinde"""
        value = scale.get_value()
        print(f"Canlılık: {value:.1f}")
        # TODO: Paleti yeniden hesapla

    def on_brightness_changed(self, scale):
        """Parlaklık değiştiğinde"""
        value = scale.get_value()
        print(f"Parlaklık: {value:.1f}")
        # TODO: Paleti yeniden hesapla

    def on_create_theme(self, button):
        """Tema oluştur ve uygula"""
        if not self.selected_wallpaper or not self.extracted_palette:
            return

        # Loading state
        self.apply_btn.set_sensitive(False)
        original_label = self.apply_btn.get_label()
        mode_text = "Light" if self.light_mode else "Dark"
        self.apply_btn.set_label(f"Tema Oluşturuluyor ({mode_text})...")

        try:
            wallpaper_name = os.path.basename(self.selected_wallpaper)

            print(f"\n{'='*60}")
            print(f"TEMA OLUŞTURULUYOR: {wallpaper_name} ({mode_text} mode)")
            print('='*60)

            # Tema oluşturucuyu başlat - light_mode parametresini de geç
            generator = ThemeGenerator(self.extracted_palette, wallpaper_name, light_mode=self.light_mode)

            # Seçili temaları kaydet
            saved_paths = {}

            if self.hyprland_switch.get_active():
                saved_paths['hyprland'] = generator.save_hyprland_colors()

            if self.waybar_switch.get_active():
                saved_paths['waybar'] = generator.save_waybar_theme()

            if self.rofi_switch.get_active():
                saved_paths['rofi'] = generator.save_rofi_theme()

            if self.kitty_switch.get_active():
                saved_paths['kitty'] = generator.save_kitty_theme()

            # Wallpaper'ı değiştir
            if self.change_wallpaper_switch.get_active():
                print("\nWallpaper değiştiriliyor...")
                success = self.wallpaper_manager.set_wallpaper(
                    self.selected_wallpaper,
                    transition="fade",
                    duration=2
                )
                if success:
                    print("Wallpaper değiştirildi")
                    self.load_current_wallpaper()

            # Temaları uygula
            print("\nTemalar uygulanıyor...")
            generator.apply_all_themes(
                hyprland=self.hyprland_switch.get_active(),
                waybar=self.waybar_switch.get_active(),
                kitty=self.kitty_switch.get_active(),
                rofi=self.rofi_switch.get_active()
            )

            print(f"\n{'='*60}")
            print("TEMA BAŞARIYLA OLUŞTURULDU VE UYGULANDI!")
            print('='*60)

            # Başarı mesajı
            self.show_success_dialog(
                "Tema Uygulandı",
                f"'{wallpaper_name}' için tema başarıyla oluşturuldu ve uygulandı!\n\n" +
                f"Kaydedilen dosyalar:\n" +
                "\n".join([f"  {k}: {v}" for k, v in saved_paths.items()])
            )

        except Exception as e:
            import traceback
            print(f"\nHATA: {e}")
            traceback.print_exc()

            self.show_error_dialog(
                "Hata",
                f"Tema oluşturulurken bir hata oluştu:\n\n{str(e)}"
            )

        finally:
            self.apply_btn.set_sensitive(True)
            self.apply_btn.set_label(original_label)

    def show_success_dialog(self, title, message):
        """Başarı dialogu göster"""
        dialog = Adw.MessageDialog.new(self.get_root())
        dialog.set_heading(title)
        dialog.set_body(message)
        dialog.add_response("ok", "Tamam")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present()

    def show_error_dialog(self, title, message):
        """Hata dialogu göster"""
        dialog = Adw.MessageDialog.new(self.get_root())
        dialog.set_heading(title)
        dialog.set_body(message)
        dialog.add_response("ok", "Tamam")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present()

    def open_waypaper(self, button):
        """Waypaper'ı aç"""
        try:
            import subprocess
            subprocess.Popen(["waypaper"])
        except Exception as e:
            print(f"Waypaper açılamadı: {e}")
