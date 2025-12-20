# app.py - TAM HALİ
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from kishi_settings.window import MainWindow
from kishi_settings.config import KishiConfig

class KishiSettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='com.ozhan.kishisettings',
            flags=0
        )
        self.kishi_config = KishiConfig()
    
    def do_startup(self):
        """Uygulama başlatılırken"""
        Gtk.Application.do_startup(self)
        
        # Config'den light_mode durumunu oku
        style_manager = Adw.StyleManager.get_default()
        if self.kishi_config.light_mode:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
    
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()
    
    def update_color_scheme(self, light_mode):
        """Color scheme'i runtime'da güncelle"""
        style_manager = Adw.StyleManager.get_default()
        if light_mode:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

def main():
    app = KishiSettingsApp()
    return app.run(sys.argv)