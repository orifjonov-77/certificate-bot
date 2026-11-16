import json
import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"C:\Users\777 comp service\Desktop\certificate"
QUESTIONS_FILE = os.path.join(BASE_DIR, "data", "questions.json")
OUTPUT_PDF = os.path.join(BASE_DIR, "MDev_Test_Javoblari_Barcha_Yonalishlar.pdf")

def get_font(size: int, bold: bool = False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "arial.ttf", "DejaVuSans.ttf"]
    for fn in font_names:
        for path in [fn, f"C:\\Windows\\Fonts\\{fn}", f"/usr/share/fonts/truetype/dejavu/{fn}"]:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        w = draw.textlength(test_line, font=font)
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_pdf_pages():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # A4 o'lchami: 300 DPI da 2480 x 3508 piksel
    page_width, page_height = 2480, 3508
    margin_x = 140
    content_width = page_width - 2 * margin_x

    f_title = get_font(68, bold=True)
    f_sub = get_font(34)
    f_h2 = get_font(44, bold=True)
    f_q = get_font(32, bold=True)
    f_ans_badge = get_font(30, bold=True)
    f_opt = get_font(28)
    f_opt_bold = get_font(28, bold=True)
    f_meta = get_font(24)

    pages = []
    
    def new_page():
        img = Image.new("RGB", (page_width, page_height), "#ffffff")
        return img

    # Har bir yo'nalishni alohida chiroyli sahifalarga taqsimlaymiz
    # 20 ta savol 2 ta sahifaga (10 tadan) toza va chiroyli joylashadi
    for d_idx, (d_key, d_info) in enumerate(data.items(), 1):
        d_title = d_info.get("title", d_key)
        questions = d_info.get("questions", [])

        # 2 sahifaga bo'lamiz: 1-10 va 11-20
        chunks = [questions[:10], questions[10:]]

        for chunk_idx, q_chunk in enumerate(chunks):
            page = new_page()
            draw = ImageDraw.Draw(page)

            # 1. Header (Yuqori panel)
            draw.rectangle([margin_x, 100, page_width - margin_x, 220], fill="#0a0a23")
            draw.text((page_width // 2, 160), f"MDEV ACADEMY  |  TEST JAVOBLARI", fill="#ffffff", font=f_h2, anchor="mm")

            # Yo'nalish sarlavhasi
            part_str = " (1-qism: 1 - 10 savollar)" if chunk_idx == 0 else " (2-qism: 11 - 20 savollar)"
            dir_full_title = f"{d_idx}. {d_title.upper()}{part_str}"
            draw.text((margin_x, 260), dir_full_title, fill="#0a0a23", font=f_h2)
            draw.line([(margin_x, 320), (page_width - margin_x, 320)], fill="#d4af37", width=5)

            y = 350
            for q in q_chunk:
                q_id = q.get("id")
                q_text = f"{q_id}. {q.get('question', '')}"
                ans = q.get("answer", "")
                opts = q.get("options", {})

                # Savol matni o'rashi
                q_lines = wrap_text(q_text, f_q, content_width - 240, draw)
                q_box_h = max(len(q_lines) * 44 + 110, 150)

                # Savol foni
                draw.rounded_rectangle([margin_x, y, page_width - margin_x, y + q_box_h], radius=15, fill="#f8f9fa", outline="#dcdcdc", width=2)

                # To'g'ri javob yashil badge
                badge_w, badge_h = 200, 60
                badge_x = page_width - margin_x - badge_w - 20
                badge_y = y + 20
                draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=10, fill="#198754")
                draw.text((badge_x + badge_w // 2, badge_y + badge_h // 2), f"JAVOB: {ans}", fill="#ffffff", font=f_ans_badge, anchor="mm")

                # Savol yozuvi
                cur_qy = y + 25
                for line in q_lines:
                    draw.text((margin_x + 25, cur_qy), line, fill="#111111", font=f_q)
                    cur_qy += 44

                # Variantlar (A, B, C, D)
                opt_y = cur_qy + 15
                opt_texts = []
                for k in ["A", "B", "C", "D"]:
                    if k in opts:
                        val = opts[k]
                        if len(val) > 35:
                            val = val[:33] + "..."
                        if k == ans:
                            opt_texts.append((f"[{k}] {val} ✓", True))
                        else:
                            opt_texts.append((f"({k}) {val}", False))

                # Variantlarni 2 ustunga taqsimlash
                col1_x = margin_x + 30
                col2_x = margin_x + content_width // 2 + 10
                for i, (ot, is_corr) in enumerate(opt_texts):
                    ox = col1_x if i % 2 == 0 else col2_x
                    oy = opt_y + (i // 2) * 40
                    color = "#0f5132" if is_corr else "#555555"
                    f_to_use = f_opt_bold if is_corr else f_opt
                    draw.text((ox, oy), ot, fill=color, font=f_to_use)

                y += q_box_h + 30

            # Footer
            draw.line([(margin_x, page_height - 150), (page_width - margin_x, page_height - 150)], fill="#cccccc", width=2)
            draw.text((margin_x, page_height - 110), "MDev Academy — Malakani baholash va sertifikatlash markazi (https://mdevsayt.uz)", fill="#777777", font=f_meta)
            draw.text((page_width - margin_x, page_height - 110), f"Yo'nalish: {d_title}", fill="#777777", font=f_meta, anchor="ra")

            pages.append(page)

    # Barcha sahifalarni bitta mukammal PDF ga yig'ish
    if pages:
        first_page = pages[0]
        first_page.save(
            OUTPUT_PDF,
            "PDF",
            resolution=300.0,
            save_all=True,
            append_images=pages[1:]
        )
        print(f"Mukammal PDF fayl tayyorlandi: {OUTPUT_PDF}")

if __name__ == "__main__":
    create_pdf_pages()
