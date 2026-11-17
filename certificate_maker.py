import os
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app.config import OUTPUT_DIR, MDEV_URL

logger = logging.getLogger(__name__)

try:
    import qrcode
except ImportError:
    qrcode = None

def get_font(size: int, bold: bool = False):
    """
    Har qanday tizimda (Linux / Render / Windows) 100% xatosiz ishlaydigan font yuklovchi.
    Hech qachon xato bermaydi!
    """
    candidates = []
    if bold:
        candidates = [
            "DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "arialbd.ttf"
        ]
    else:
        candidates = [
            "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "arial.ttf"
        ]

    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue

    # Agar hech qaysi topilmasa, default font
    return ImageFont.load_default()


def draw_ribbon_badge(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    """freeCodeCamp sertifikatidagi kabi o'ng pastki burchakdagi medalli nishon"""
    badge_color = "#0a0a23"
    r = 65
    
    # Chap lenta
    draw.polygon([
        (cx - 35, cy + 20),
        (cx - 50, cy + 120),
        (cx - 25, cy + 100),
        (cx - 10, cy + 120),
        (cx - 10, cy + 20)
    ], fill=badge_color)
    
    # O'ng lenta
    draw.polygon([
        (cx + 10, cy + 20),
        (cx + 10, cy + 120),
        (cx + 25, cy + 100),
        (cx + 50, cy + 120),
        (cx + 35, cy + 20)
    ], fill=badge_color)

    # Doiralar
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=badge_color, outline="#ffffff", width=3)
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline="#ffffff", width=2)

    font_icon = get_font(32, bold=True)
    draw.text((cx, cy - 2), "( M )", fill="#ffffff", font=font_icon, anchor="mm")


def draw_signature(draw: ImageDraw.ImageDraw, x: int, y: int):
    """freeCodeCamp uslubidagi vektorli chiroyli imzo"""
    sig_color = "#0a0a23"
    pts_list = [
        [(x - 60, y + 10), (x - 45, y - 35), (x - 20, y - 45), (x - 10, y + 5), (x - 50, y + 15), (x + 10, y - 30)],
        [(x + 10, y - 30), (x + 20, y + 10), (x + 35, y - 20), (x + 50, y + 5), (x + 65, y - 15)],
        [(x - 70, y - 5), (x - 30, y - 50), (x - 20, y + 25), (x + 80, y - 40)]
    ]
    for pts in pts_list:
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=sig_color, width=3)


def generate_qr_code(url: str, size: int = 180) -> Image.Image:
    """Xatosiz kvadrat QR kod"""
    if qrcode is not None:
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0a0a23", back_color="#ffffff").convert("RGBA")
            return img.resize((size, size))
        except Exception as e:
            logger.error(f"QR yaratishda ogohlantirish: {e}")

    # Zaxira chiroyli QR placeholder
    placeholder = Image.new("RGBA", (size, size), "#ffffff")
    p_draw = ImageDraw.Draw(placeholder)
    p_draw.rectangle([0, 0, size-1, size-1], outline="#0a0a23", width=3)
    p_draw.text((size // 2, size // 2), "MDEV QR", fill="#0a0a23", anchor="mm")
    return placeholder


def make_certificate(full_name: str, course: str, score: int, cert_id: int, user_id: int) -> str:
    """
    Aynan foydalanuvchi taqdim etgan PDF (freeCodeCamp) uslubidagi 100% professional sertifikat
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width, height = 1920, 1360
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    # Shriftlarni o'lcham bo'yicha xavfsiz yuklaymiz
    font_brand = get_font(50, bold=True)
    font_certifies = get_font(34, bold=False)
    font_name = get_font(68, bold=True)
    font_sub_comp = get_font(34, bold=False)
    font_course = get_font(72, bold=True)
    font_details = get_font(32, bold=False)
    font_hours = get_font(26, bold=False)
    font_signer_name = get_font(28, bold=True)
    font_signer_title = get_font(24, bold=False)
    font_verify_lbl = get_font(20, bold=False)
    font_verify_url = get_font(22, bold=False)

    # 1. Tashqi to'q ko'k hoshiya
    border_color = "#0a0a23"
    border_margin = 40
    border_width = 12
    draw.rectangle(
        [border_margin, border_margin, width - border_margin, height - border_margin],
        outline=border_color,
        width=border_width
    )

    # 2. Yuqori to'q ko'k lenta (Header bar)
    header_top = border_margin + border_width
    header_height = 110
    draw.rectangle(
        [header_top, header_top, width - header_top, header_top + header_height],
        fill=border_color
    )
    
    # Header matni: mdev ( • ) academy
    draw.text((width // 2, header_top + header_height // 2), "mdev( flame ) academy", fill="#ffffff", font=font_brand, anchor="mm")

    # 3. Asosiy matnlar (Markazda)
    draw.text((width // 2, 275), "This certifies that", fill="#3b3a30", font=font_certifies, anchor="mm")

    # Ism va Familiya
    clean_name = " ".join(full_name.split())
    formatted_name = " ".join([word.capitalize() for word in clean_name.split()])
    draw.text((width // 2, 365), formatted_name, fill="#0a0a23", font=font_name, anchor="mm")

    draw.text((width // 2, 455), "successfully completed the", fill="#3b3a30", font=font_sub_comp, anchor="mm")

    # Kurs nomi
    draw.text((width // 2, 545), course, fill="#0a0a23", font=font_course, anchor="mm")

    # Sana
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    now = datetime.now()
    month_name = months[now.month - 1]
    date_str = f"{month_name} {now.day}, {now.year}"
    
    details_line = f"Developer Certification on {date_str}"
    draw.text((width // 2, 635), details_line, fill="#3b3a30", font=font_details, anchor="mm")

    sub_details = f"representing approximately {score * 15} hours of coursework and examination (Score: {score}/20)"
    draw.text((width // 2, 695), sub_details, fill="#616161", font=font_hours, anchor="mm")

    # 4. Imzo qismi
    sig_center_x = width // 2
    sig_center_y = 820
    draw_signature(draw, sig_center_x, sig_center_y - 20)
    draw.line([(sig_center_x - 180, sig_center_y + 15), (sig_center_x + 180, sig_center_y + 15)], fill="#0a0a23", width=2)
    draw.text((sig_center_x, sig_center_y + 45), "Executive Director", fill="#0a0a23", font=font_signer_name, anchor="mm")
    draw.text((sig_center_x, sig_center_y + 80), "MDev Educational Platform", fill="#5a5a5a", font=font_signer_title, anchor="mm")

    # 5. Chap pastki burchakdagi QR kod
    base_verify_url = MDEV_URL if MDEV_URL else "https://mdevsayt.uz"
    cert_code = f"mdev-{user_id}-{cert_id:04d}"
    verify_full_url = f"{base_verify_url}/verify/{cert_code}"

    qr_size = 180
    qr_x = 110
    qr_y = 860
    qr_img = generate_qr_code(verify_full_url, size=qr_size)
    image.paste(qr_img, (qr_x, qr_y), qr_img)

    # 6. O'ng pastki burchakdagi nishon (Ribbon badge)
    badge_x = width - 190
    badge_y = 940
    draw_ribbon_badge(draw, badge_x, badge_y)

    # 7. Pastki tekshirish havolasi
    footer_y = height - 120
    draw.text((width // 2, footer_y), "Verify this certification at:", fill="#757575", font=font_verify_lbl, anchor="mm")
    draw.text((width // 2, footer_y + 30), verify_full_url, fill="#0a0a23", font=font_verify_url, anchor="mm")

    # Saqlash
    output_filename = f"cert_{user_id}_{cert_id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    rgb_image = image.convert("RGB")
    rgb_image.save(output_path, format="PNG", quality=98)
    logger.info(f"Sertifikat muvaffaqiyatli saqlandi: {output_path}")
    return output_path
