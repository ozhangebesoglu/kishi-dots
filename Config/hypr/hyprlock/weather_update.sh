#!/usr/bin/env bash

# Hava durumu verisini kaydeceğimiz dosya
CACHE_FILE="/tmp/weather_cache"

while true; do
    # Hava durumunu çek ve dosyaya yaz (Mersin)
    # Başarısız olursa dosyayı silmez, eskisini korur.
    WEATHER=$(curl -s 'wttr.in/Mersin?format=%c+%t')
    
    if [ ! -z "$WEATHER" ]; then
        echo "$WEATHER" > "$CACHE_FILE"
    fi
    
    # 30 dakika bekle (1800 saniye)
    sleep 1800
done
