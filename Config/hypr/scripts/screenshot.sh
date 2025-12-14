#!/usr/bin/env bash

# Ses çal (Freedesktop standart sesi)
# Eğer ses çıkmazsa bu satırı silebilirsin
canberra-gtk-play -i camera-shutter &

# Tarih formatı
TIME=$(date "+%Y-%m-%d-%H-%M-%S")
DIR="$HOME/Pictures/Screenshots"
FILE="$DIR/screenshot-$TIME.png"

# Klasör yoksa oluştur
mkdir -p "$DIR"

# --- Slurp Ayarları (Gruvbox Stil) ---
# -b: Arkaplan rengi (Hafif şeffaf siyah)
# -c: Kenarlık rengi (Gruvbox Turuncusu)
# -w: Kenarlık kalınlığı
# -d: Seçim yaparken diğer pencereleri dondurur (Animasyon hissi verir)

# Seçim yap ve kaydet
grim -g "$(slurp -d -c d79921 -b 282828aa -w 2)" "$FILE"

# Eğer kullanıcı iptal etmediyse (Dosya oluştuysa)
if [ -f "$FILE" ]; then
    # Panoya kopyala
    wl-copy < "$FILE"
    
    # Bildirim gönder (Resim önizlemesiyle)
    notify-send "Ekran Görüntüsü" "Kaydedildi ve Panoya Kopyalandı" -i "$FILE"
    
    # Düzenlemek için Swappy'i aç
    swappy -f "$FILE"
fi
