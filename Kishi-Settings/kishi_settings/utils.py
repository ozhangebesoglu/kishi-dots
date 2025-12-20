import sys
import os
import re

class ConfigHandler:
    def __init__(self):
        # Gerçek sistem yolu
        self.config_path = os.path.expanduser("~/.config/hypr")
        # Test için (Eğer ~/.config/hypr yoksa proje içindekini kullan)
        if not os.path.exists(self.config_path):
            # Fallback to local repo for development
            self.config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Config/hypr"))
    
    def get_file_path(self, filename):
        return os.path.join(self.config_path, filename)
    
    def read_value(self, filename, key):
        """Dosyadan belirli bir değişkenin değerini okur (örn: gaps_in)"""
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Regex: key = value (boşluklara duyarlı)
        match = re.search(rf"^\s*{key}\s*=\s*(\d+)", content, re.MULTILINE)
        if match:
            return int(match.group(1))
        return 0
    
    def write_value(self, filename, key, value):
        """Dosyadaki değişkeni günceller"""
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        with open(filepath, 'w') as f:
            for line in lines:
                if re.match(rf"^\s*{key}\s*=", line):
                    f.write(f"    {key} = {value}\n")
                else:
                    f.write(line)
    
    def get_binds(self):
        """binds.conf dosyasını okur ve listeler"""
        filepath = self.get_file_path("binds.conf")
        binds = []
        
        if not os.path.exists(filepath):
            return binds
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("bind ="):
                    # bind = MOD, KEY, ACTION, COMMAND
                    parts = line.split(",")
                    if len(parts) >= 4:
                        mod = parts[0].replace("bind =", "").strip().replace("$mainMod", "SUPER")
                        key = parts[1].strip()
                        action = parts[2].strip()
                        command = parts[3].strip()
                        
                        # Yorumları temizle
                        if "#" in command:
                            command = command.split("#")[0].strip()
                        
                        binds.append({
                            "mod": mod,
                            "key": key,
                            "action": action,
                            "command": command
                        })
        
        return binds