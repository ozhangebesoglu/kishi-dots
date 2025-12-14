#!/usr/bin/env bash
# Aktif klavye düzenini alır (TR/US vs.)
LAYOUT=$(hyprctl devices -j | jq -r '.keyboards[] | select(.main == true) | .active_keymap' | head -n 1)
echo "  $LAYOUT"
