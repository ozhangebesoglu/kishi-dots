import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk  # ← Gdk eklendi
from kishi_settings.pages.general import GeneralPage
from kishi_settings.pages.keybinds import KeybindsPage
from kishi_settings.pages.wallpaper_theme import WallpaperThemePage
from kishi_settings.pages.animations import AnimationsPage
from kishi_settings.pages.workspaces import WorkspacesPage
import os

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(900, 600)
        self.set_title("Kishi Settings")
        
        # CSS yükle
        self.load_css()
        
        # Ana İçerik: Navigation Split View
        self.split_view = Adw.NavigationSplitView()
        self.set_content(self.split_view)
        
        # Sayfaları oluştur
        self.general_page = GeneralPage()
        self.animations_page = AnimationsPage()
        self.workspaces_page = WorkspacesPage()
        self.keybinds_page = KeybindsPage()
        self.wallpaper_theme_page = WallpaperThemePage()

        # NavigationPage'leri cache'le (her sayfa için bir kez oluştur)
        self.nav_pages = {}
        
        # === SIDEBAR OLUŞTURMA ===
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("navigation-sidebar")
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        # Liste öğelerini ekle
        self.add_sidebar_row("Görünüm ve Düzen", "preferences-desktop-display-symbolic", self.general_page)
        self.add_sidebar_row("Animasyonlar", "preferences-desktop-effects-symbolic", self.animations_page)
        self.add_sidebar_row("Çalışma Alanları", "preferences-desktop-workspaces-symbolic", self.workspaces_page)
        self.add_sidebar_row("Kısayollar", "input-keyboard-symbolic", self.keybinds_page)
        self.add_sidebar_row("Duvar Kağıdı Temaları", "preferences-desktop-wallpaper-symbolic", self.wallpaper_theme_page)
        
        # ListBox tıklama eventi
        self.list_box.connect("row-activated", self.on_row_activated)
        
        # Sidebar için ToolbarView
        sidebar_toolbar = Adw.ToolbarView()
        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_show_end_title_buttons(False)
        sidebar_toolbar.add_top_bar(sidebar_header)
        sidebar_toolbar.set_content(self.list_box)
        
        # Sidebar NavigationPage
        sidebar_page = Adw.NavigationPage.new(sidebar_toolbar, "sidebar")
        sidebar_page.set_title("Ayarlar")
        self.split_view.set_sidebar(sidebar_page)
        
        # === İÇERİK SAYFALARI ===
        # Varsayılan olarak ilk sayfayı göster
        self.change_page(self.general_page, "Görünüm ve Düzen")
        
        # Split view'ı aç
        self.split_view.set_show_content(True)
        
        # İlk satırı seçili yap
        self.list_box.select_row(self.list_box.get_row_at_index(0))
    
    def add_sidebar_row(self, title, icon_name, target_page):
        row = Adw.ActionRow()
        row.set_title(title)
        row.set_use_markup(False)  # Markup'ı devre dışı bırak
        
        # İkon ekle
        icon = Gtk.Image.new_from_icon_name(icon_name)
        row.add_prefix(icon)
        row.set_activatable(True)
        
        # Page referansını row'a bağla
        row.target_page = target_page
        row.page_title = title
        
        self.list_box.append(row)
    
    def on_row_activated(self, list_box, row):
        # Seçilen satıra göre sayfayı değiştir
        if hasattr(row, 'target_page'):
            self.change_page(row.target_page, row.page_title)
    
    def change_page(self, page, title):
        # NavigationPage'i cache'den al veya oluştur
        page_id = id(page)

        if page_id not in self.nav_pages:
            # İlk kez oluştur
            tag = title.lower().replace(" ", "-").replace("&", "").replace("ı", "i").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c").replace("ğ", "g")
            nav_page = Adw.NavigationPage.new(page, tag)
            nav_page.set_title(title)
            self.nav_pages[page_id] = nav_page

        # Cache'den al ve göster
        self.split_view.set_content(self.nav_pages[page_id])
    
    def load_css(self):
        """Custom CSS yükle"""
        try:
            css_provider = Gtk.CssProvider()
            css_path = os.path.join(
                os.path.dirname(__file__), 
                "style.css"
            )
            if os.path.exists(css_path):
                css_provider.load_from_path(css_path)
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
        except Exception as e:
            print(f"CSS yükleme hatası: {e}")