#!/usr/bin/env bash
# Hyprland'den aktif pencere ismini çeker
WINDOW=$(hyprctl activewindow -j | jq -r ".class")
if [ "$WINDOW" != "null" ] && [ -n "$WINDOW" ]; then
    echo "$WINDOW"
else
    echo "Masaüstü"
fi
