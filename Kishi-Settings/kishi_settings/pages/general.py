import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from kishi_settings.utils import ConfigHandler
import subprocess

class GeneralPage(Adw.PreferencesPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Görünüm ve Düzen")  
        self.set_icon_name("preferences-desktop-display-symbolic")
        
        self.config = ConfigHandler()
        
        # --- Grup: Boşluklar (Gaps) ---
        gaps_group = Adw.PreferencesGroup(title="Boşluklar (Gaps)")
        self.add(gaps_group)
        
        # Gaps In
        self.gaps_in_row = Adw.SpinRow(title="İç Boşluk (Gaps In)")
        self.gaps_in_row.set_subtitle("Pencereler arası mesafe")
        self.gaps_in_row.set_range(0, 50)
        # set_increments() YOK - adjustment kullan
        adj = self.gaps_in_row.get_adjustment()
        adj.set_step_increment(1)
        adj.set_page_increment(5)
        self.gaps_in_row.set_value(self.config.read_value("general.conf", "gaps_in") or 10)
        self.gaps_in_row.connect("notify::value", self.on_gaps_in_changed)
        gaps_group.add(self.gaps_in_row)
        
        # Gaps Out
        self.gaps_out_row = Adw.SpinRow(title="Dış Boşluk (Gaps Out)")
        self.gaps_out_row.set_subtitle("Ekran kenarı mesafesi")
        self.gaps_out_row.set_range(0, 100)
        # set_increments() YOK - adjustment kullan
        adj = self.gaps_out_row.get_adjustment()
        adj.set_step_increment(1)
        adj.set_page_increment(5)
        self.gaps_out_row.set_value(self.config.read_value("general.conf", "gaps_out") or 30)
        self.gaps_out_row.connect("notify::value", self.on_gaps_out_changed)
        gaps_group.add(self.gaps_out_row)
        
        # --- Grup: Kenarlıklar (Borders) ---
        border_group = Adw.PreferencesGroup(title="Kenarlıklar")
        self.add(border_group)
        
        # Border Size
        self.border_row = Adw.SpinRow(title="Kenarlık Kalınlığı")
        self.border_row.set_range(0, 10)
        # set_increments() YOK - adjustment kullan
        adj = self.border_row.get_adjustment()
        adj.set_step_increment(1)
        adj.set_page_increment(1)
        self.border_row.set_value(self.config.read_value("general.conf", "border_size") or 2)
        self.border_row.connect("notify::value", self.on_border_changed)
        border_group.add(self.border_row)
        
        # Rounding
        self.rounding_row = Adw.SpinRow(title="Köşe Yuvarlaklığı (Rounding)")
        self.rounding_row.set_range(0, 50)
        # set_increments() YOK - adjustment kullan
        adj = self.rounding_row.get_adjustment()
        adj.set_step_increment(1)
        adj.set_page_increment(5)
        self.rounding_row.set_value(self.config.read_value("decoration.conf", "rounding") or 10)
        self.rounding_row.connect("notify::value", self.on_rounding_changed)
        border_group.add(self.rounding_row)
    
    def on_gaps_in_changed(self, widget, _):
        val = int(widget.get_value())
        self.config.write_value("general.conf", "gaps_in", val)
        self.reload_hyprland()
    
    def on_gaps_out_changed(self, widget, _):
        val = int(widget.get_value())
        self.config.write_value("general.conf", "gaps_out", val)
        self.reload_hyprland()
    
    def on_border_changed(self, widget, _):
        val = int(widget.get_value())
        self.config.write_value("general.conf", "border_size", val)
        self.reload_hyprland()
    
    def on_rounding_changed(self, widget, _):
        val = int(widget.get_value())
        self.config.write_value("decoration.conf", "rounding", val)
        self.reload_hyprland()
    
    def reload_hyprland(self):
        # Hyprland'i anlık güncellemek için komut gönder
        try:
            subprocess.run(["hyprctl", "reload"], check=False)
        except Exception as e:
            print(f"Hyprland reload hatası: {e}")