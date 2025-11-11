"""Allow running packgen as python -m app.packgen"""
from .cli import main
import sys

if __name__ == '__main__':
    sys.exit(main())
