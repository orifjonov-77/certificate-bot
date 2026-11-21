from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Any

def get_admin_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Adminlikni tasdiqlash uchun telefon raqam jo'natish tugmasi"""
    kb = [
        [KeyboardButton(text="📱 Telefon raqamimni tasdiqlash", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli menyusi"""
    buttons = [
        [InlineKeyboardButton(text="📝 Savollarni boshqarish", callback_data="admin:manage_questions")],
        [InlineKeyboardButton(text="👥 Adminlarni ko'rish / qo'shish", callback_data="admin:manage_admins")],
        [InlineKeyboardButton(text="📊 Bot statistikasi", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🔙 Foydalanuvchi rejimi", callback_data="admin:exit")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_directions_keyboard(directions: List[Dict[str, str]], action: str = "view") -> InlineKeyboardMarkup:
    """Savollarni boshqarish uchun yo'nalishlar ro'yxati"""
    buttons = []
    row = []
    for item in directions:
        btn = InlineKeyboardButton(
            text=f"{item['title']}", 
            callback_data=f"adm_dir:{action}:{item['id']}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Admin menyuga qaytish", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_questions_list_keyboard(direction_id: str, questions: List[Dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    """Yo'nalishdagi savollar ro'yxati (har sahifada 5 tadan)"""
    per_page = 5
    total_pages = max(1, (len(questions) + per_page - 1) // per_page)
    start = page * per_page
    end = start + per_page
    chunk = questions[start:end]

    buttons = []
    for q in chunk:
        btn_text = f"❓ {q['id']}. {q['question'][:30]}..."
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"adm_q:{direction_id}:{q['id']}")])

    # Yangi savol qo'shish
    buttons.append([InlineKeyboardButton(text="➕ Yangi savol qo'shish", callback_data=f"adm_add_q:{direction_id}")])

    # Navigatsiya sahifalari
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"adm_page:{direction_id}:{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"adm_page:{direction_id}:{page+1}"))
    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(text="🔙 Yo'nalishlarga qaytish", callback_data="admin:manage_questions")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_question_actions_keyboard(direction_id: str, q_id: int) -> InlineKeyboardMarkup:
    """Aynan bitta savol ustida amallar (Tahrirlash / O'chirish)"""
    buttons = [
        [InlineKeyboardButton(text="✏️ Savolni tahrirlash", callback_data=f"adm_edit_q:{direction_id}:{q_id}")],
        [InlineKeyboardButton(text="🗑 Savolni o'chirish", callback_data=f"adm_del_q:{direction_id}:{q_id}")],
        [InlineKeyboardButton(text="🔙 Savollar ro'yxatiga qaytish", callback_data=f"adm_dir:view:{direction_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_management_keyboard(admins: list) -> InlineKeyboardMarkup:
    """Adminlar ro'yxati va yangi admin qo'shish"""
    buttons = []
    for adm in admins:
        phone = adm["phone"]
        role = adm["role"]
        adm_id = adm["id"]
        status = "⭐️ Asosiy" if role == "superadmin" else "👤 Admin"
        txt = f"{status}: {phone}"
        btn_row = [InlineKeyboardButton(text=txt, callback_data="ignore")]
        if role != "superadmin":
            btn_row.append(InlineKeyboardButton(text="❌ O'chirish", callback_data=f"adm_del_admin:{adm_id}"))
        buttons.append(btn_row)

    buttons.append([InlineKeyboardButton(text="➕ Yangi admin qo'shish (Telefon orqali)", callback_data="adm_add_admin")])
    buttons.append([InlineKeyboardButton(text="🔙 Admin menyuga qaytish", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_answer_select_keyboard() -> InlineKeyboardMarkup:
    """To'g'ri javobni tanlash tugmalari"""
    buttons = [
        [
            InlineKeyboardButton(text="A", callback_data="ans_pick:A"),
            InlineKeyboardButton(text="B", callback_data="ans_pick:B"),
            InlineKeyboardButton(text="C", callback_data="ans_pick:C"),
            InlineKeyboardButton(text="D", callback_data="ans_pick:D")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
