import subprocess
import os

try:
    os.chdir(r"C:\Users\777 comp service\Desktop\certificate")
    # update_questions.py ni chaqirib yangilaymiz
    subprocess.run(["python", "update_questions.py"], check=False)
    
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "Add full Admin Panel with CRUD and hard professional exam questions"],
        ["git", "push", "origin", "main"]
    ]
    for cmd in commands:
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Bajarildi: {' '.join(cmd)}")
    print("\n>>> Muvaffaqiyatli: Yangi Admin Panel va qiyin testlar GitHub ga push bo'ldi! <<<")
except Exception as e:
    print(f"Xatolik: {e}")
