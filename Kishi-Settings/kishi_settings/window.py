import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from kishi_settings.pages.general import GeneralPage
from kishi_settings.pages.keybinds import KeybindsPage

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(900, 600)
        self.set_title("Kishi Settings")
        
        # Ana İçerik: Navigation Split View
        self.split_view = Adw.NavigationSplitView()
        self.set_content(self.split_view)
        
        # Sayfaları oluştur
        self.general_page = GeneralPage()
        self.keybinds_page = KeybindsPage()
        
        # === SIDEBAR OLUŞTURMA ===
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("navigation-sidebar")
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        # Liste öğelerini ekle (& yerine ve kullan)
        self.add_sidebar_row("Görünüm ve Düzen", "preferences-desktop-display-symbolic", self.general_page)
        self.add_sidebar_row("Kısayollar", "input-keyboard-symbolic", self.keybinds_page)
        
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
        # Yeni NavigationPage oluştur ve başlığı ayarla
        nav_page = Adw.NavigationPage.new(page, title.lower().replace(" ", "-").replace("&", ""))
        nav_page.set_title(title)
        self.split_view.set_content(nav_page)