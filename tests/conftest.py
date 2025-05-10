import sys
from pathlib import Path

# Добавляем корень проекта в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))