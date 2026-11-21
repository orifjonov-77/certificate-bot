import aiosqlite
import os
from datetime import datetime
from app.config import DB_PATH

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # Adminlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE,
                user_id INTEGER UNIQUE,
                role TEXT DEFAULT 'admin',
                added_at TIMESTAMP NOT NULL
            )
        """)
        # Boshlang'ich admin telefonlarini kiritish
        from app.config import DEFAULT_ADMIN_PHONES
        now = datetime.now().isoformat()
        for p in ["+998951932546", "+998889810206"]:
            await db.execute(
                "INSERT OR IGNORE INTO admins (phone, role, added_at) VALUES (?, 'superadmin', ?)",
                (p, now)
            )

        # Test natijalari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                direction_id TEXT NOT NULL,
                direction_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                completed_at TIMESTAMP NOT NULL,
                scheduled_notify_at TIMESTAMP NOT NULL,
                is_notified INTEGER DEFAULT 0
            )
        """)
        # Sertifikat berilgan foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                full_name TEXT NOT NULL,
                issued_at TIMESTAMP NOT NULL,
                certificate_path TEXT NOT NULL,
                test_result_id INTEGER UNIQUE
            )
        """)
        # Eski bazadan qolgan bo'lsa ustunlarni avtomatik qo'shish (migratsiya)
        try:
            await db.execute("ALTER TABLE certificates ADD COLUMN test_result_id INTEGER UNIQUE")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE certificates ADD COLUMN course TEXT")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE certificates ADD COLUMN certificate_path TEXT")
        except Exception:
            pass

        # Foydalanuvchining ayni vaqtda faol testi bormi-yo'qligini tekshirish uchun jadval
        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_sessions (
                user_id INTEGER PRIMARY KEY,
                direction_id TEXT NOT NULL,
                direction_name TEXT NOT NULL,
                current_question INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                answers_json TEXT DEFAULT '[]',
                started_at TIMESTAMP NOT NULL
            )
        """)
        await db.commit()

async def get_active_session(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM active_sessions WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def create_active_session(user_id: int, direction_id: str, direction_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        await db.execute(
            """INSERT OR REPLACE INTO active_sessions 
               (user_id, direction_id, direction_name, current_question, score, started_at) 
               VALUES (?, ?, ?, 0, 0, ?)""",
            (user_id, direction_id, direction_name, now)
        )
        await db.commit()

async def update_active_session(user_id: int, current_question: int, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE active_sessions SET current_question = ?, score = ? WHERE user_id = ?",
            (current_question, score, user_id)
        )
        await db.commit()

async def delete_active_session(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))
        await db.commit()

async def save_test_result(user_id: int, direction_id: str, direction_name: str, score: int, total_questions: int, scheduled_notify_at: datetime):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            """INSERT INTO test_results 
               (user_id, direction_id, direction_name, score, total_questions, completed_at, scheduled_notify_at, is_notified)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (user_id, direction_id, direction_name, score, total_questions, now, scheduled_notify_at.isoformat())
        )
        await db.commit()
        return cursor.lastrowid

async def get_pending_results():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM test_results WHERE is_notified = 0"
        ) as cursor:
            return await cursor.fetchall()

async def mark_result_notified(result_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE test_results SET is_notified = 1 WHERE id = ?", (result_id,))
        await db.commit()

async def get_certificate_by_test_result(test_result_id: int):
    """Bitta test natijasi bo'yicha allaqachon sertifikat berilganligini tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM certificates WHERE test_result_id = ?", (test_result_id,)
        ) as cursor:
            return await cursor.fetchone()

async def save_certificate(user_id: int, course: str, full_name: str, certificate_path: str, test_result_id: int):
    """Sertifikat ma'lumotlarini bazada saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            """INSERT INTO certificates (user_id, course, direction_name, full_name, issued_at, certificate_path, test_result_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, course, course, full_name, now, certificate_path, test_result_id)
        )
        await db.commit()
        return cursor.lastrowid

# ================= ADMIN FUNKSIYALARI =================
async def is_admin(user_id: int) -> bool:
    """Foydalanuvchi user_id bo'yicha admin ekanligini tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM admins WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def verify_admin_by_phone(user_id: int, phone: str) -> bool:
    """Kontakt ulashganda telefon raqami adminlar ro'yxatida bo'lsa user_id ni bog'lash"""
    # Raqamni tozalash (+998901234567 formatiga keltirish)
    clean_phone = phone.strip()
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Telefon raqami bazada bormi?
        async with db.execute("SELECT id FROM admins WHERE phone = ? OR phone = ?", (clean_phone, clean_phone.replace("+", ""))) as cursor:
            row = await cursor.fetchone()
            if row:
                await db.execute("UPDATE admins SET user_id = ? WHERE id = ?", (user_id, row[0]))
                await db.commit()
                return True
    return False

async def add_admin_phone(phone: str) -> bool:
    """Yangi admin telefon raqamini kiritish"""
    clean_phone = phone.strip()
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        try:
            await db.execute(
                "INSERT INTO admins (phone, role, added_at) VALUES (?, 'admin', ?)",
                (clean_phone, now)
            )
            await db.commit()
            return True
        except Exception:
            return False

async def get_all_admins():
    """Barcha adminlarni ro'yxatini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM admins ORDER BY id ASC") as cursor:
            return await cursor.fetchall()

async def remove_admin_by_id(admin_id: int):
    """Adminni o'chirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE id = ? AND role != 'superadmin'", (admin_id,))
        await db.commit()

