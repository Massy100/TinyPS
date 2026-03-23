import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.app import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTiny PhotoShop cerrada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)