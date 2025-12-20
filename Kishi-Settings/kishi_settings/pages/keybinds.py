import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from kishi_settings.utils import ConfigHandler

class KeybindsPage(Adw.PreferencesPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Kısayollar")
        self.set_icon_name("input-keyboard-symbolic")
        
        self.config = ConfigHandler()
        
        group = Adw.PreferencesGroup(title="Tanımlı Kısayollar")
        self.add(group)
        
        binds = self.config.get_binds()
        
        for bind in binds:
            row = Adw.ActionRow()
            
            # Başlık: Tuş Kombinasyonu (Örn: SUPER + T)
            mod_text = bind['mod']
            key_text = bind['key'].upper()
            row.set_title(f"{mod_text} + {key_text}")
            
            # Alt Başlık: Komut
            cmd_display = bind['command']
            if "$terminal" in cmd_display:
                cmd_display = "Terminal"
            elif "$fileManager" in cmd_display:
                cmd_display = "Dosya Yöneticisi"
            elif "rofi" in cmd_display:
                cmd_display = "Rofi Menü"
            
            row.set_subtitle(cmd_display)
            
            # İkon
            icon_name = "system-run-symbolic"
            if "exec" in bind['action']:
                icon_name = "system-run-symbolic"
            elif "kill" in bind['action']:
                icon_name = "window-close-symbolic"
            elif "workspace" in bind['action']:
                icon_name = "go-jump-symbolic"
                
            row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
            
            group.add(row)
