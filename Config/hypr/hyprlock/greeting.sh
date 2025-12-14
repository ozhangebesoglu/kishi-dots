#!/usr/bin/env bash
HOUR=$(date +%H)
if [ $HOUR -lt 12 ]; then
    echo "Günaydın, $USER"
elif [ $HOUR -lt 18 ]; then
    echo "Tünaydın, $USER"
else
    echo "İyi Geceler, $USER"
fi
