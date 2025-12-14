#!/usr/bin/env bash

####### Değişkenler #######
# Casper laptoplarda genelde BAT0 veya BAT1 olur, otomatik bulsun:
BATTERY_PATH=$(find /sys/class/power_supply/ -name "BAT*" | head -n 1)

####### Kontrol #######
if [[ -d "$BATTERY_PATH" ]]; then
    STATUS=$(cat "$BATTERY_PATH/status")
    CAPACITY=$(cat "$BATTERY_PATH/capacity")

    if [[ "$STATUS" == "Charging" ]]; then
        echo "󰂄 $CAPACITY%"
    else
        # Pil seviyesine göre ikon seçimi
        if [[ $CAPACITY -ge 90 ]]; then ICON=""
        elif [[ $CAPACITY -ge 60 ]]; then ICON=""
        elif [[ $CAPACITY -ge 40 ]]; then ICON=""
        elif [[ $CAPACITY -ge 15 ]]; then ICON=""
        else ICON=""; fi
        
        echo "$ICON $CAPACITY%"
    fi
else
    echo "" # Pil yoksa boş dön
fi
