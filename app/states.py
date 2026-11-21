from aiogram.fsm.state import State, StatesGroup

class QuizStates(StatesGroup):
    answering = State()       # Foydalanuvchi savollarga javob berayotgan holat
    awaiting_name = State()   # Sertifikat uchun ism-familiya kiritish holati

class AdminStates(StatesGroup):
    awaiting_new_admin_phone = State() # Yangi admin telefon raqami
    # Savol tahrirlash/qo'shish bosqichlari
    awaiting_question_text = State()
    awaiting_option_a = State()
    awaiting_option_b = State()
    awaiting_option_c = State()
    awaiting_option_d = State()
    awaiting_correct_answer = State()

