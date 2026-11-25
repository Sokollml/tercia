"""pytest bootstrap: добавляем модули collector/ и validator/src в sys.path,
чтобы тесты импортировали их как плоские модули без установки пакета.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
for rel in ("collector", os.path.join("validator", "src")):
    path = os.path.join(ROOT, rel)
    if path not in sys.path:
        sys.path.insert(0, path)
