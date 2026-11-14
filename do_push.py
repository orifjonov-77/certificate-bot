import subprocess
import os

try:
    os.chdir(r"C:\Users\777 comp service\Desktop\certificate")
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "Debug token loading and strip whitespace"],
        ["git", "push", "origin", "main"]
    ]
    for cmd in commands:
        subprocess.run(cmd, capture_output=True, text=True)
    print("\n>>> Kod GitHub ga push qilindi! <<<")
except Exception as e:
    print(f"Xatolik: {e}")
