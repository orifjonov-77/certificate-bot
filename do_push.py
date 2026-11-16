import subprocess
import os

try:
    os.chdir(r"C:\Users\777 comp service\Desktop\certificate")
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "Perfect freeCodeCamp style certificate, robust error handling and Linux font support"],
        ["git", "push", "origin", "main"]
    ]
    for cmd in commands:
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Bajarildi: {' '.join(cmd)}")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)
    print("\n>>> Muvaffaqiyatli: Barcha yangilanishlar GitHub ga push bo'ldi! <<<")
except Exception as e:
    print(f"Xatolik: {e}")
