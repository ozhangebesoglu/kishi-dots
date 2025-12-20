# kishi_settings/pages/workspaces.py
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import json
import threading


class WorkspacesPage(Adw.PreferencesPage):
    """Hyprland workspace yönetimi sayfası"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Çalışma Alanları")
        self.set_icon_name("preferences-desktop-workspaces-symbolic")

        self.workspaces = []
        self.monitors = []

        # === Mevcut Durumu ===
        status_group = Adw.PreferencesGroup(
            title="Aktif Çalışma Alanları",
            description="Şu an açık olan workspace'ler"
        )
        self.add(status_group)

        # Workspace listesi için container
        self.workspace_list_box = Gtk.ListBox()
        self.workspace_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.workspace_list_box.add_css_class("boxed-list")

        status_group.add(self.workspace_list_box)

        # Yenile butonu
        refresh_row = Adw.ActionRow()
        refresh_row.set_title("Listeyi Yenile")

        refresh_btn = Gtk.Button(label="Yenile")
        refresh_btn.set_valign(Gtk.Align.CENTER)
        refresh_btn.connect("clicked", self.refresh_workspaces)
        refresh_row.add_suffix(refresh_btn)
        status_group.add(refresh_row)

        # === Monitör Bilgisi ===
        monitor_group = Adw.PreferencesGroup(
            title="Monitör Bilgisi",
            description="Bağlı ekranlar ve özellikleri"
        )
        self.add(monitor_group)

        self.monitor_list_box = Gtk.ListBox()
        self.monitor_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.monitor_list_box.add_css_class("boxed-list")
        monitor_group.add(self.monitor_list_box)

        # === Workspace Ayarları ===
        settings_group = Adw.PreferencesGroup(
            title="Workspace Ayarları",
            description="Çalışma alanı davranışları"
        )
        self.add(settings_group)

        # Varsayılan workspace sayısı
        default_count_row = Adw.ActionRow()
        default_count_row.set_title("Varsayılan Workspace Sayısı")
        default_count_row.set_subtitle("Başlangıçta oluşturulacak workspace sayısı")

        self.workspace_count_spin = Gtk.SpinButton.new_with_range(1, 20, 1)
        self.workspace_count_spin.set_value(10)
        self.workspace_count_spin.set_valign(Gtk.Align.CENTER)
        default_count_row.add_suffix(self.workspace_count_spin)
        settings_group.add(default_count_row)

        # Boş workspace'leri kapat
        self.auto_close_switch = Adw.SwitchRow(
            title="Boş Workspace'leri Otomatik Kapat",
            subtitle="Pencere kalmayan workspace'ler otomatik kapanır"
        )
        self.auto_close_switch.set_active(False)
        settings_group.add(self.auto_close_switch)

        # Workspace geçişlerinde wrap
        self.wrap_switch = Adw.SwitchRow(
            title="Döngüsel Geçiş",
            subtitle="Son workspace'ten ilke, ilkten sona geçiş"
        )
        self.wrap_switch.set_active(False)
        settings_group.add(self.wrap_switch)

        # === Hızlı Aksiyonlar ===
        actions_group = Adw.PreferencesGroup(
            title="Hızlı Aksiyonlar",
            description="Workspace yönetim komutları"
        )
        self.add(actions_group)

        # Yeni workspace oluştur
        new_ws_row = Adw.ActionRow()
        new_ws_row.set_title("Yeni Workspace Oluştur")
        new_ws_row.set_subtitle("Boş bir workspace aç ve oraya geç")

        new_ws_btn = Gtk.Button(label="Oluştur")
        new_ws_btn.add_css_class("suggested-action")
        new_ws_btn.set_valign(Gtk.Align.CENTER)
        new_ws_btn.connect("clicked", self.create_new_workspace)
        new_ws_row.add_suffix(new_ws_btn)
        actions_group.add(new_ws_row)

        # Tüm boş workspace'leri kapat
        close_empty_row = Adw.ActionRow()
        close_empty_row.set_title("Boş Workspace'leri Kapat")
        close_empty_row.set_subtitle("Penceresi olmayan tüm workspace'leri kapat")

        close_empty_btn = Gtk.Button(label="Kapat")
        close_empty_btn.add_css_class("destructive-action")
        close_empty_btn.set_valign(Gtk.Align.CENTER)
        close_empty_btn.connect("clicked", self.close_empty_workspaces)
        close_empty_row.add_suffix(close_empty_btn)
        actions_group.add(close_empty_row)

        # === Özel Workspace'ler ===
        special_group = Adw.PreferencesGroup(
            title="Özel Workspace'ler",
            description="Scratchpad ve özel amaçlı workspace'ler"
        )
        self.add(special_group)

        # Scratchpad
        scratchpad_row = Adw.ActionRow()
        scratchpad_row.set_title("Scratchpad")
        scratchpad_row.set_subtitle("Gizli terminal workspace'i (SUPER + S)")

        scratchpad_btn = Gtk.Button(label="Aç/Kapat")
        scratchpad_btn.set_valign(Gtk.Align.CENTER)
        scratchpad_btn.connect("clicked", self.toggle_scratchpad)
        scratchpad_row.add_suffix(scratchpad_btn)
        special_group.add(scratchpad_row)

        # İlk yükleme
        self.refresh_workspaces(None)

    def refresh_workspaces(self, button):
        """Workspace ve monitör listesini yenile"""
        # Arka planda yükle
        thread = threading.Thread(target=self._load_workspace_data, daemon=True)
        thread.start()

    def _load_workspace_data(self):
        """Arka planda workspace verilerini yükle"""
        try:
            # Workspace'leri al
            result = subprocess.run(
                ['hyprctl', 'workspaces', '-j'],
                capture_output=True, text=True
            )
            self.workspaces = json.loads(result.stdout) if result.stdout else []

            # Monitörleri al
            result = subprocess.run(
                ['hyprctl', 'monitors', '-j'],
                capture_output=True, text=True
            )
            self.monitors = json.loads(result.stdout) if result.stdout else []

            # UI'ı güncelle
            GLib.idle_add(self._update_workspace_list)
            GLib.idle_add(self._update_monitor_list)

        except Exception as e:
            print(f"Workspace verisi yükleme hatası: {e}")

    def _update_workspace_list(self):
        """Workspace listesini güncelle"""
        # Mevcut öğeleri temizle
        child = self.workspace_list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.workspace_list_box.remove(child)
            child = next_child

        # Workspace'leri sırala
        sorted_ws = sorted(self.workspaces, key=lambda x: x.get('id', 0))

        for ws in sorted_ws:
            ws_id = ws.get('id', 0)
            ws_name = ws.get('name', str(ws_id))
            monitor = ws.get('monitor', 'Bilinmiyor')
            windows = ws.get('windows', 0)
            last_title = ws.get('lastwindowtitle', '')

            # Row oluştur
            row = Adw.ActionRow()
            row.set_title(f"Workspace {ws_name}")

            # Pencere sayısı ve son başlık
            if windows > 0:
                subtitle = f"{windows} pencere • {last_title[:40]}..." if len(last_title) > 40 else f"{windows} pencere • {last_title}"
            else:
                subtitle = "Boş"
            row.set_subtitle(subtitle)

            # İkon
            if windows > 0:
                icon = Gtk.Image.new_from_icon_name("window-symbolic")
            else:
                icon = Gtk.Image.new_from_icon_name("window-close-symbolic")
            row.add_prefix(icon)

            # Git butonu
            go_btn = Gtk.Button()
            go_btn.set_icon_name("go-next-symbolic")
            go_btn.set_valign(Gtk.Align.CENTER)
            go_btn.add_css_class("flat")
            go_btn.connect("clicked", self.go_to_workspace, ws_id)
            go_btn.set_tooltip_text(f"Workspace {ws_id}'e git")
            row.add_suffix(go_btn)

            self.workspace_list_box.append(row)

    def _update_monitor_list(self):
        """Monitör listesini güncelle"""
        # Mevcut öğeleri temizle
        child = self.monitor_list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.monitor_list_box.remove(child)
            child = next_child

        for monitor in self.monitors:
            name = monitor.get('name', 'Bilinmiyor')
            desc = monitor.get('description', '')
            width = monitor.get('width', 0)
            height = monitor.get('height', 0)
            refresh = monitor.get('refreshRate', 0)
            active_ws = monitor.get('activeWorkspace', {}).get('name', '?')
            focused = monitor.get('focused', False)

            row = Adw.ActionRow()
            row.set_title(f"{name}" + (" (Aktif)" if focused else ""))
            row.set_subtitle(f"{width}x{height} @ {refresh:.0f}Hz • Workspace: {active_ws}")

            # İkon
            icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            row.add_prefix(icon)

            self.monitor_list_box.append(row)

    def go_to_workspace(self, button, ws_id):
        """Belirtilen workspace'e git"""
        subprocess.run(['hyprctl', 'dispatch', 'workspace', str(ws_id)])
        print(f"Workspace {ws_id}'e gidildi")

    def create_new_workspace(self, button):
        """Yeni boş workspace oluştur"""
        # En yüksek ID'yi bul ve +1 ekle
        max_id = max([ws.get('id', 0) for ws in self.workspaces], default=0)
        new_id = max_id + 1

        subprocess.run(['hyprctl', 'dispatch', 'workspace', str(new_id)])
        print(f"Workspace {new_id} oluşturuldu")

        # Listeyi yenile
        self.refresh_workspaces(None)

    def close_empty_workspaces(self, button):
        """Boş workspace'leri kapat"""
        closed = 0
        for ws in self.workspaces:
            if ws.get('windows', 0) == 0:
                ws_id = ws.get('id', 0)
                # Aktif workspace değilse kapat
                subprocess.run([
                    'hyprctl', 'dispatch', 'workspace', f'name:{ws_id}'
                ])
                closed += 1

        print(f"{closed} boş workspace kapatıldı")
        self.refresh_workspaces(None)

    def toggle_scratchpad(self, button):
        """Scratchpad'i aç/kapat"""
        subprocess.run(['hyprctl', 'dispatch', 'togglespecialworkspace'])
        print("Scratchpad toggle edildi")
