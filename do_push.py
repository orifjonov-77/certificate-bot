import subprocess
import os

try:
    os.chdir(r"C:\Users\777 comp service\Desktop\certificate")
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "Support Render Free Web Service with health check port"],
        ["git", "push", "origin", "main"]
    ]
    for cmd in commands:
        res = subprocess.run(cmd, capture_output=True, text=True)
    print("\n>>> GitHub yangilandi! Endi bepul Web Service tanlay olasiz! <<<")
except Exception as e:
    print(f"Xatolik: {e}")
