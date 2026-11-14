import os
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app.config import TEMPLATE_PATH, OUTPUT_DIR, MDEV_URL

logger = logging.getLogger(__name__)

try:
    import qrcode
except ImportError:
    qrcode = None

def get_font(name: str, size: int):
    """Windows va boshqa tizimlarda shriftlarni xavfsiz yuklash"""
    font_paths = [
        name,
        f"C:\\Windows\\Fonts\\{name}",
        f"C:\\Windows\\Fonts\\arial.ttf",
        f"C:\\Windows\\Fonts\\times.ttf"
    ]
    for p in font_paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def create_default_template(path: str = TEMPLATE_PATH):
    """
    Mukammal, hashamatli premium dizayndagi sertifikat shablonini generatsiya qiladi.
    1920x1080 Full HD
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    width, height = 1920, 1080

    # To'q ko'k va chuqur gradient uslubidagi fon
    image = Image.new("RGB", (width, height), "#080e1e")
    draw = ImageDraw.Draw(image)

    # Bezak ranglari (Hashamatli oltin ranglar palitrasi)
    gold_main = "#d4af37"      # Asosiy sof oltin
    gold_bright = "#f3e5ab"    # Ochiq oltin
    gold_dark = "#997a15"      # To'q oltin
    accent_blue = "#00d2ff"    # Texnologik moviy urg'u

    # 1. Tashqi nozik oltin hoshiyalar
    draw.rectangle([35, 35, width - 35, height - 35], outline=gold_dark, width=2)
    draw.rectangle([45, 45, width - 45, height - 45], outline=gold_main, width=4)
    draw.rectangle([55, 55, width - 55, height - 55], outline="#17223b", width=2)
    draw.rectangle([70, 70, width - 70, height - 70], outline=gold_main, width=2)

    # 2. To'rtta burchakdagi geometrik hashamatli burchak bezaklari
    c_size = 90
    corners = [
        (70, 70), 
        (width - 70, 70), 
        (70, height - 70), 
        (width - 70, height - 70)
    ]
    for cx, cy in corners:
        # Kichik romb/kvadratlar
        draw.rectangle([cx - 16, cy - 16, cx + 16, cy + 16], fill="#080e1e", outline=gold_main, width=3)
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=gold_main)

    # 3. Markaziy fon uchun xira naqshsimon kontur
    draw.rectangle([120, 120, width - 120, height - 120], outline="#101c38", width=1)

    # Shriftlar
    font_brand = get_font("arialbd.ttf", 60)
    font_sub_brand = get_font("arial.ttf", 22)
    font_title = get_font("georgiab.ttf", 76)
    font_intro = get_font("ariali.ttf", 26)
    font_roles = get_font("arialbd.ttf", 22)
    font_meta_lbl = get_font("arial.ttf", 18)

    # Sarlavha: MDEV ACADEMY
    draw.text((width // 2, 175), "MDEV ACADEMY", fill=accent_blue, font=font_brand, anchor="mm")
    draw.text((width // 2, 230), "MALAKANI BAHOLASH VA SERTIFIKATLASHTIRISH MARKAZI", fill="#8a99ad", font=font_sub_brand, anchor="mm")

    # Markaziy Oltin ajratuvchi chiziq va olmos
    draw.line([(width // 2 - 350, 275), (width // 2 - 25, 275)], fill=gold_main, width=2)
    draw.line([(width // 2 + 25, 275), (width // 2 + 350, 275)], fill=gold_main, width=2)
    draw.polygon([(width // 2, 268), (width // 2 + 10, 275), (width // 2, 282), (width // 2 - 10, 275)], fill=gold_main)

    # SERTIFIKAT yozuvi
    draw.text((width // 2, 355), "SERTIFIKAT", fill=gold_bright, font=font_title, anchor="mm")
    draw.text((width // 2, 425), "Ushbu sertifikat muvaffaqiyatli topshirilgan test natijasiga ko'ra taqdim etiladi:", fill="#c5d1e0", font=font_intro, anchor="mm")

    # 4. O'ng tarafdagi Imzolar va Markaziy Muhr
    # O'ng tarafdagi tasdiqlovchi imzolar bloki
    right_x = width - 360
    draw.line([(right_x - 170, 920), (right_x + 170, 920)], fill=gold_main, width=2)
    draw.text((right_x, 948), "MDev Bosh Mutaxassisi", fill="#ffffff", font=font_roles, anchor="mm")
    draw.text((right_x, 975), "Imzo va Tasdiq", fill="#8a99ad", font=font_meta_lbl, anchor="mm")

    # Markazdagi MDev Rasmiy Muhri
    seal_cx = width // 2 + 40
    seal_cy = 910
    draw.ellipse([seal_cx - 65, seal_cy - 65, seal_cx + 65, seal_cy + 65], outline=gold_main, width=3)
    draw.ellipse([seal_cx - 57, seal_cy - 57, seal_cx + 57, seal_cy + 57], outline=gold_dark, width=1)
    font_seal_b = get_font("arialbd.ttf", 20)
    font_seal_s = get_font("arial.ttf", 15)
    draw.text((seal_cx, seal_cy - 16), "★ MDEV ★", fill=gold_bright, font=font_seal_b, anchor="mm")
    draw.text((seal_cx, seal_cy + 12), "VERIFIED", fill=accent_blue, font=font_seal_s, anchor="mm")
    draw.text((seal_cx, seal_cy + 30), "ACADEMY", fill=gold_dark, font=font_seal_s, anchor="mm")

    image.save(path, format="PNG")
    logger.info(f"Yangi sertifikat shabloni yaratildi: {path}")


def generate_qr_code(url: str, size: int = 150) -> Image.Image:
    """Oltin hoshiyali va oq fonli toza QR kod generatsiya qiladi"""
    if qrcode is not None:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#080e1e", back_color="#ffffff").convert("RGBA")
        return img.resize((size, size))
    else:
        placeholder = Image.new("RGBA", (size, size), "#ffffff")
        p_draw = ImageDraw.Draw(placeholder)
        p_draw.text((size // 2, size // 2), "QR KOD", fill="#000000", anchor="mm")
        return placeholder


def make_certificate(full_name: str, course: str, score: int, cert_id: int, user_id: int) -> str:
    """
    Foydalanuvchi ma'lumotlari, chap pastki burchakdagi aniq QR kod bilan Full HD mukammal sertifikat yaratadi.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Har doim mukammal shablonni yangilab olish
    create_default_template(TEMPLATE_PATH)

    image = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Shriftlar
    font_name = get_font("arialbd.ttf", 66)
    font_body = get_font("arial.ttf", 32)
    font_course = get_font("arialbd.ttf", 38)
    font_meta = get_font("arial.ttf", 26)
    font_qr_title = get_font("arialbd.ttf", 17)
    font_qr_url = get_font("arial.ttf", 15)

    # 1. Ism-familiya (Oq rang, markazda)
    clean_name = " ".join(full_name.split())
    draw.text((width // 2, 530), clean_name.upper(), fill="#ffffff", font=font_name, anchor="mm")

    # Ism ostiga chiroyli oltin chiziq
    name_w = len(clean_name) * 22
    line_w = min(max(name_w, 300), 800)
    draw.line([(width // 2 - line_w // 2, 580), (width // 2 + line_w // 2, 580)], fill="#d4af37", width=2)

    # 2. Yo'nalish va natija
    body_text_1 = f"\"{course}\" yo'nalishi bo'yicha nazariy va amaliy test savollarini"
    draw.text((width // 2, 635), body_text_1, fill="#b0c5e0", font=font_body, anchor="mm")

    body_text_2 = f"muvaffaqiyatli topshirdi va  {score} / 20 ball  to'pladi."
    draw.text((width // 2, 685), body_text_2, fill="#00d2ff", font=font_course, anchor="mm")

    # 3. Sana va Sertifikat raqami
    date_str = datetime.now().strftime("%d.%m.%Y")
    cert_no = f"MDEV-{cert_id:05d}"
    meta_text = f"Berilgan sana: {date_str}      |      Sertifikat №: {cert_no}"
    draw.text((width // 2, 755), meta_text, fill="#e5c158", font=font_meta, anchor="mm")

    # 4. CHAP PASTKI BURCHAKDAGI QR KOD (140x140 o'lchamda, qat'iy chap pastda)
    target_url = MDEV_URL if MDEV_URL else "https://mdevsayt.uz"
    qr_size = 145
    qr_x = 120       # Chap burchak
    qr_y = 835       # Pastki qism

    # QR kod uchun oq fonga ega zamonaviy kartochka orqa foni
    card_padding = 10
    draw.rectangle(
        [qr_x - card_padding, qr_y - card_padding, qr_x + qr_size + card_padding, qr_y + qr_size + card_padding + 35],
        fill="#0d172e",
        outline="#d4af37",
        width=2
    )

    qr_img = generate_qr_code(target_url, size=qr_size)
    image.paste(qr_img, (qr_x, qr_y), qr_img)

    # QR kod ostidagi yozuvlar
    draw.text((qr_x + qr_size // 2, qr_y + qr_size + 15), "SKANER QILING", fill="#00d2ff", font=font_qr_title, anchor="mm")
    draw.text((qr_x + qr_size // 2, qr_y + qr_size + 30), "Rasmiy tekshirish", fill="#a0b2c6", font=font_qr_url, anchor="mm")

    # Xavfsiz fayl saqlash
    output_filename = f"cert_{user_id}_{cert_id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    rgb_image = image.convert("RGB")
    rgb_image.save(output_path, format="PNG", quality=98)
    logger.info(f"Mukammal sertifikat generatsiya qilindi: {output_path}")
    return output_path
