import os
import sys

# Enable UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

EXCLUDE = {"env", "__pycache__", ".venv", ".git"}

def print_tree(folder, prefix=""):
    items = sorted([i for i in os.listdir(folder) if i not in EXCLUDE])

    for index, item in enumerate(items):
        path = os.path.join(folder, item)
        is_last = index == len(items) - 1

        print(prefix + ("└── " if is_last else "├── ") + item)

        if os.path.isdir(path):
            print_tree(path, prefix + ("    " if is_last else "│   "))

backend_folder = "backend"

print(backend_folder)
print_tree(backend_folder)