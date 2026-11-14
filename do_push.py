import subprocess
import os

try:
    os.chdir(r"C:\Users\777 comp service\Desktop\certificate")
    commands = [
        ["git", "init"],
        ["git", "branch", "-M", "main"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit: Perfect MDev Certificate Bot for Render"],
        ["git", "remote", "remove", "origin"],
        ["git", "remote", "add", "origin", "https://github.com/orifjonov-77/certificate-bot.git"],
        ["git", "push", "-u", "origin", "main", "--force"]
    ]
    for cmd in commands:
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Bajarildi: {' '.join(cmd)}")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)
    print("\n>>> Muvaffaqiyatli: certificate-bot ga to'liq push bo'ldi! <<<")
except Exception as e:
    print(f"Xatolik: {e}")
