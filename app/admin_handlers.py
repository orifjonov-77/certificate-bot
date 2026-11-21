import logging
import re
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from app import database
from app.states import AdminStates
from app.questions_loader import (
    get_directions,
    get_questions_for_direction,
    get_direction_title,
    add_or_update_question,
    delete_question,
    load_questions
)
from app.admin_keyboards import (
    get_admin_phone_request_keyboard,
    get_admin_main_keyboard,
    get_admin_directions_keyboard,
    get_admin_questions_list_keyboard,
    get_admin_question_actions_keyboard,
    get_admin_management_keyboard,
    get_admin_answer_select_keyboard
)

logger = logging.getLogger(__name__)
admin_router = Router()

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()

    # 1. User allaqachon adminmi?
    if await database.is_admin(user_id):
        await message.answer(
            f"👑 <b>MDev Admin Boshqaruv Paneliga xush kelibsiz!</b>\n\n"
            f"Bu yerda siz:\n"
            f"• Savollarni ko'rish, tahrirlash, o'chirish va yangi savol qo'shish;\n"
            f"• Yangi adminlarni qo'shish va boshqarish imkoniga egasiz.",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="HTML"
        )
        return

    # 2. Agar user_id ulanmagan bo'lsa, telefon raqamini so'raymiz
    text = (
        "🔐 <b>Adminlikni tasdiqlash</b>\n\n"
        "Siz admin ro'yxatida ekanligingizni tasdiqlash uchun pastdagi "
        "<b>'📱 Telefon raqamimni tasdiqlash'</b> tugmasini bosing:"
    )
    await message.answer(text, reply_markup=get_admin_phone_request_keyboard(), parse_mode="HTML")

@admin_router.message(F.contact)
async def on_contact_received(message: Message):
    user_id = message.from_user.id
    contact = message.contact

    if contact.user_id != user_id:
        await message.answer("⚠️ Iltimos, faqat o'zingizning shaxsiy profilingizga ulangan raqamni yuboring!")
        return

    phone = contact.phone_number
    # Adminlikni tekshirish va bog'lash
    is_verified = await database.verify_admin_by_phone(user_id, phone)
    if is_verified:
        await message.answer(
            f"✅ <b>Tabriklaymiz! Telefon raqamingiz ({phone}) muvaffaqiyatli tasdiqlandi.</b>\n"
            f"Sizga adminlik huquqlari berildi!",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
        await message.answer(
            "👑 <b>MDev Admin Boshqaruv Paneli:</b>",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"❌ Sizning telefon raqamingiz ({phone}) ruxsat etilgan adminlar ro'yxatida topilmadi.\n"
            f"Ruxsat olish uchun asosiy adminga murojaat qiling.",
            reply_markup=ReplyKeyboardRemove()
        )

@admin_router.callback_query(F.data == "admin:menu")
async def on_admin_menu(callback: CallbackQuery, state: FSMContext):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        "👑 <b>MDev Admin Boshqaruv Paneli:</b>",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_router.callback_query(F.data == "admin:exit")
async def on_admin_exit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Foydalanuvchi rejimiga qaytildi. Test topshirish uchun: /start")
    await callback.answer()

@admin_router.callback_query(F.data == "admin:stats")
async def on_admin_stats(callback: CallbackQuery):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return
    
    total_tests = 0
    total_certs = 0
    total_users = 0
    try:
        async with database.aiosqlite.connect(database.DB_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM test_results") as c1:
                row1 = await c1.fetchone()
                total_tests = row1[0] if row1 else 0
            async with db.execute("SELECT COUNT(*) FROM certificates") as c2:
                row2 = await c2.fetchone()
                total_certs = row2[0] if row2 else 0
            async with db.execute("SELECT COUNT(DISTINCT user_id) FROM test_results") as c3:
                row3 = await c3.fetchone()
                total_users = row3[0] if row3 else 0
    except Exception as e:
        logger.error(f"Statistika olishda xatolik: {e}")

    stats_text = (
        f"📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 Test topshirgan foydalanuvchilar: <b>{total_users} ta</b>\n"
        f"📝 Jami topshirilgan testlar: <b>{total_tests} ta</b>\n"
        f"🎓 Berilgan sertifikatlar: <b>{total_certs} ta</b>\n\n"
        f"⚡️ <i>Tizim holati: Faol va uzluksiz ishlamoqda</i>"
    )
    buttons = [[InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:menu")]]
    try:
        await callback.message.edit_text(stats_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    except Exception:
        await callback.message.answer(stats_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await callback.answer()

# ================= ADMINLARNI BOSHQARISH =================
@admin_router.callback_query(F.data == "admin:manage_admins")
async def on_manage_admins(callback: CallbackQuery):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    admins = await database.get_all_admins()
    text = (
        "👥 <b>Adminlar ro'yxati:</b>\n\n"
        "Yangi admin qo'shish uchun pastdagi tugmani bosing va uning telefon raqamini yozing:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_management_keyboard(admins), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "adm_add_admin")
async def on_add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(AdminStates.awaiting_new_admin_phone)
    text = (
        "➕ <b>Yangi admin qo'shish</b>\n\n"
        "Iltimos, yangi adminning telefon raqamini xalqaro formatda kiriting:\n"
        "<i>Masalan: +998901234567</i>"
    )
    buttons = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:manage_admins")]]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminStates.awaiting_new_admin_phone)
async def on_new_admin_phone_entered(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+?[0-9]{9,15}$", phone):
        await message.answer("⚠️ Telefon raqam formati noto'g'ri! Qaytadan kiriting (masalan: +998901234567):")
        return
    success = await database.add_admin_phone(phone)
    if success:
        await message.answer(f"✅ <b>{phone}</b> raqami muvaffaqiyatli adminlar ro'yxatiga qo'shildi!\nUshbu foydalanuvchi botga kirib /admin buyrug'ini bosa oladi.")
    else:
        await message.answer(f"⚠️ Ushbu raqam ({phone}) allaqachon adminlar ro'yxatida mavjud!")
    
    await state.clear()
    admins = await database.get_all_admins()
    await message.answer("👥 <b>Adminlar ro'yxati:</b>", reply_markup=get_admin_management_keyboard(admins), parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("adm_del_admin:"))
async def on_delete_admin(callback: CallbackQuery):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    admin_id = int(callback.data.split(":")[1])
    await database.remove_admin_by_id(admin_id)
    await callback.answer("Admin muvaffaqiyatli o'chirildi.")
    admins = await database.get_all_admins()
    await callback.message.edit_text("👥 <b>Adminlar ro'yxati yangilandi:</b>", reply_markup=get_admin_management_keyboard(admins), parse_mode="HTML")

# ================= SAVOLLARNI BOSHQARISH =================
@admin_router.callback_query(F.data == "admin:manage_questions")
async def on_manage_questions_directions(callback: CallbackQuery):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    directions = get_directions()
    text = "📚 <b>Savollarni tahrirlash yoki o'chirish uchun yo'nalishni tanlang:</b>"
    await callback.message.edit_text(text, reply_markup=get_admin_directions_keyboard(directions), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("adm_dir:view:"))
async def on_direction_questions_view(callback: CallbackQuery):
    if not await database.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return
    direction_id = callback.data.split(":")[2]
    questions = get_questions_for_direction(direction_id)
    dir_title = get_direction_title(direction_id)
    text = f"📂 <b>{dir_title}</b> yo'nalishidagi savollar (Jami: {len(questions)} ta):\nBatafsil ko'rish yoki tahrirlash uchun savolni tanlang:"
    await callback.message.edit_text(text, reply_markup=get_admin_questions_list_keyboard(direction_id, questions, page=0), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("adm_page:"))
async def on_questions_page(callback: CallbackQuery):
    parts = callback.data.split(":")
    direction_id = parts[1]
    page = int(parts[2])
    questions = get_questions_for_direction(direction_id)
    dir_title = get_direction_title(direction_id)
    text = f"📂 <b>{dir_title}</b> yo'nalishidagi savollar (Jami: {len(questions)} ta):"
    await callback.message.edit_text(text, reply_markup=get_admin_questions_list_keyboard(direction_id, questions, page=page), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("adm_q:"))
async def on_single_question_view(callback: CallbackQuery):
    parts = callback.data.split(":")
    direction_id = parts[1]
    q_id = int(parts[2])
    questions = get_questions_for_direction(direction_id)
    target_q = next((q for q in questions if q["id"] == q_id), None)
    if not target_q:
        await callback.answer("Savol topilmadi!", show_alert=True)
        return

    text = (
        f"❓ <b>Savol #{target_q['id']}:</b>\n\n"
        f"{target_q['question']}\n\n"
        f"<b>Variantlar:</b>\n"
        f"A) {target_q['options'].get('A')}\n"
        f"B) {target_q['options'].get('B')}\n"
        f"C) {target_q['options'].get('C')}\n"
        f"D) {target_q['options'].get('D')}\n\n"
        f"✅ <b>To'g'ri javob:</b> {target_q['answer']}"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_question_actions_keyboard(direction_id, q_id), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("adm_del_q:"))
async def on_delete_question(callback: CallbackQuery):
    parts = callback.data.split(":")
    direction_id = parts[1]
    q_id = int(parts[2])
    deleted = delete_question(direction_id, q_id)
    if deleted:
        await callback.answer(f"Savol #{q_id} o'chirildi!", show_alert=True)
    else:
        await callback.answer("O'chirishda xatolik yuz berdi.", show_alert=True)
    
    questions = get_questions_for_direction(direction_id)
    dir_title = get_direction_title(direction_id)
    text = f"📂 <b>{dir_title}</b> yo'nalishidagi savollar (Jami: {len(questions)} ta):"
    await callback.message.edit_text(text, reply_markup=get_admin_questions_list_keyboard(direction_id, questions, page=0), parse_mode="HTML")

# ================= SAVOL TAHRIRLASH VA QO'SHISH BOSQICHLARI =================
@admin_router.callback_query(F.data.startswith("adm_edit_q:") | F.data.startswith("adm_add_q:"))
async def on_start_edit_or_add_q(callback: CallbackQuery, state: FSMContext):
    is_edit = callback.data.startswith("adm_edit_q:")
    parts = callback.data.split(":")
    direction_id = parts[1]
    q_id = int(parts[2]) if is_edit else None

    await state.set_state(AdminStates.awaiting_question_text)
    await state.update_data(direction_id=direction_id, question_id=q_id, is_edit=is_edit)

    action_name = f"Savol #{q_id} ni tahrirlash" if is_edit else "Yangi savol qo'shish"
    prompt = (
        f"📝 <b>{action_name}</b>\n\n"
        f"1-qadam: Iltimos, <b>savol matnini</b> yuboring:"
    )
    buttons = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"adm_dir:view:{direction_id}")]]
    await callback.message.edit_text(prompt, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminStates.awaiting_question_text)
async def on_question_text_entered(message: Message, state: FSMContext):
    await state.update_data(q_text=message.text.strip())
    await state.set_state(AdminStates.awaiting_option_a)
    await message.answer("2-qadam: <b>A variant</b> matnini yuboring:", parse_mode="HTML")

@admin_router.message(AdminStates.awaiting_option_a)
async def on_opt_a_entered(message: Message, state: FSMContext):
    await state.update_data(opt_a=message.text.strip())
    await state.set_state(AdminStates.awaiting_option_b)
    await message.answer("3-qadam: <b>B variant</b> matnini yuboring:", parse_mode="HTML")

@admin_router.message(AdminStates.awaiting_option_b)
async def on_opt_b_entered(message: Message, state: FSMContext):
    await state.update_data(opt_b=message.text.strip())
    await state.set_state(AdminStates.awaiting_option_c)
    await message.answer("4-qadam: <b>C variant</b> matnini yuboring:", parse_mode="HTML")

@admin_router.message(AdminStates.awaiting_option_c)
async def on_opt_c_entered(message: Message, state: FSMContext):
    await state.update_data(opt_c=message.text.strip())
    await state.set_state(AdminStates.awaiting_option_d)
    await message.answer("5-qadam: <b>D variant</b> matnini yuboring:", parse_mode="HTML")

@admin_router.message(AdminStates.awaiting_option_d)
async def on_opt_d_entered(message: Message, state: FSMContext):
    await state.update_data(opt_d=message.text.strip())
    await state.set_state(AdminStates.awaiting_correct_answer)
    await message.answer("6-qadam: <b>To'g'ri javobni tanlang:</b>", reply_markup=get_admin_answer_select_keyboard(), parse_mode="HTML")

@admin_router.callback_query(AdminStates.awaiting_correct_answer, F.data.startswith("ans_pick:"))
async def on_correct_answer_picked(callback: CallbackQuery, state: FSMContext):
    ans = callback.data.split(":")[1]
    data = await state.get_data()
    direction_id = data["direction_id"]
    q_id = data["question_id"]
    q_text = data["q_text"]
    options = {
        "A": data["opt_a"],
        "B": data["opt_b"],
        "C": data["opt_c"],
        "D": data["opt_d"]
    }

    add_or_update_question(direction_id, q_id, q_text, options, ans)
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ <b>Savol muvaffaqiyatli saqlandi!</b>\n\n"
        f"❓ {q_text}\n"
        f"✅ To'g'ri javob: <b>{ans}</b>",
        parse_mode="HTML"
    )
    
    questions = get_questions_for_direction(direction_id)
    dir_title = get_direction_title(direction_id)
    await callback.message.answer(
        f"📂 <b>{dir_title}</b> yo'nalishidagi savollar ro'yxati:",
        reply_markup=get_admin_questions_list_keyboard(direction_id, questions, page=0),
        parse_mode="HTML"
    )
    await callback.answer()
