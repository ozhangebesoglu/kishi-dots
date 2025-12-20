import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from kishi_settings.window import MainWindow

class KishiSettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='com.ozhan.kishisettings',
            flags=0
        )
    
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

def main():
    app = KishiSettingsApp()
    return app.run(sys.argv)