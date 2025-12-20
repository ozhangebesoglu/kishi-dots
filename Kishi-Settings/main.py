import sys
import os

# Proje kök dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kishi_settings.app import main

if __name__ == '__main__':
    sys.exit(main())
