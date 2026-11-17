import subprocess
import os

try:
    os.chdir(r"C:\Users\777 comp service\Desktop\certificate")
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "Fix import create_default_template error completely"],
        ["git", "push", "origin", "main"]
    ]
    for cmd in commands:
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Bajarildi: {' '.join(cmd)}")
    print("\n>>> Muvaffaqiyatli: Render uchun tuzatish GitHub ga push bo'ldi! <<<")
except Exception as e:
    print(f"Xatolik: {e}")
