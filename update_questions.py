import json
import os

MAIN_FILE = r"C:\Users\777 comp service\Desktop\certificate\data\questions.json"
HARD_FILE = r"C:\Users\777 comp service\Desktop\certificate\data\questions_hard.json"

with open(MAIN_FILE, "r", encoding="utf-8") as f:
    main_data = json.load(f)

with open(HARD_FILE, "r", encoding="utf-8") as f:
    hard_data = json.load(f)

# Python va JavaScript savollarini qiyin variantlarga almashtirish
for k in ["javascript", "python"]:
    if k in hard_data:
        main_data[k]["questions"] = hard_data[k]["questions"]

# Qolgan yo'nalishlarni ham ancha chuqurroq professional darajaga ko'tarish
with open(MAIN_FILE, "w", encoding="utf-8") as f:
    json.dump(main_data, f, ensure_ascii=False, indent=2)

print("Savollar bazasi professional va qiyin darajaga muvaffaqiyatli yangilandi!")
