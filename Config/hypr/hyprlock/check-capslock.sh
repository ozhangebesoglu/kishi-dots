#!/usr/bin/env bash

# Klavyelerin durumunu kontrol et
# Eğer herhangi bir klavyede Caps Lock açıksa uyarı ver
if hyprctl devices | grep "Caps Lock: on" > /dev/null; then
    echo "󰪛 CAPS LOCK"
else
    echo ""
fi
