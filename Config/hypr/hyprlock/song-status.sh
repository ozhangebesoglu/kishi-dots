#!/usr/bin/env bash

# playerctl yüklü mü ve müzik çalıyor mu kontrol et
if command -v playerctl &> /dev/null; then
    STATUS=$(playerctl status 2>/dev/null)
    
    if [[ "$STATUS" == "Playing" ]]; then
        # Şarkı ve Sanatçı bilgisini al (Uzunsa kısalt)
        METADATA=$(playerctl metadata --format '{{title}}  •  {{artist}}')
        if [[ ${#METADATA} -gt 50 ]]; then
            echo "  ${METADATA:0:50}..."
        else
            echo "  $METADATA"
        fi
    else
        echo "" # Çalmıyorsa boş dön
    fi
else
    echo ""
fi
