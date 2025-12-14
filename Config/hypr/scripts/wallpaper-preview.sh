#!/usr/bin/env bash

# --- AYARLAR ---
WALL_DIR="$HOME/Pictures/Wallpapers/wallpaper"

# --- MEVCUT DUVAR KAĞIDINI KAYDET (ESC için) ---
CURRENT_WALL=$(swww query | grep -oP "image: \K.*" | head -n 1)

# --- RENKLER (Gruvbox) ---
FG="#ebdbb2"
BG="#282828"
HL="#d79921"
PROMPT="#fb4934"

# Dosya yoluna git
cd "$WALL_DIR" || exit

# --- FZF BAŞLAT ---
# --bind 'focus:...' -> Listede her hareket ettiğinde (odak değiştiğinde) komutu çalıştırır.
# execute-silent -> Komutu arka planda çalıştırır, ekrana bir şey basmaz.
# transform-header -> Üst kısma kaç dosya olduğunu yazar (İsteğe bağlı görsel detay).

SELECTED=$(find . -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) -printf "%P\n" | sort | fzf \
    --bind "focus:execute-silent(swww img \"$WALL_DIR/{}\" --transition-type grow --transition-pos 0.5,0.5 --transition-step 90 --transition-fps 60)" \
    --bind "enter:print(selected)+accept" \
    --bind "esc:print(cancel)+abort" \
    --header "Haraket Ettikçe Değişir | ESC: İptal | ENTER: Seç" \
    --layout=reverse \
    --border=rounded \
    --margin=5% \
    --prompt="Duvar Kağıdı > " \
    --pointer="" \
    --marker=">" \
    --color=fg:$FG,bg:$BG,hl:$HL,prompt:$PROMPT)

# --- SONUÇ KONTROLÜ ---
# Çıktıda 'selected' kelimesi yoksa (yani ESC veya Ctrl+C yapıldıysa)
if [[ "$SELECTED" != *"selected"* ]]; then
    echo "İptal edildi. Eski duvar kağıdına dönülüyor..."
    if [ -n "$CURRENT_WALL" ]; then
        swww img "$CURRENT_WALL" --transition-type fade
    fi
else
    # Eğer seçildiyse dosya isminden 'selected' kısmını temizleyelim (fzf bazen bitişik verebilir)
    # Ancak bind ile print(selected) kullandığımız için fzf sadece "selected" basabilir, 
    # asıl dosya o an focus olandır.
    
    # KESİN ÇÖZÜM: Focus zaten resmi değiştirdi. ENTER sadece onaylamak içindi.
    # Yani ekstra bir swww komutu çalıştırmamıza gerek yok, son kalan resim ekranda kalır.
    
    notify-send "Duvar Kağıdı" "Seçim Onaylandı."
fi
