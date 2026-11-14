import sqlite3
import os

DB_PATH = r"C:\Users\777 comp service\Desktop\certificate\data\database.db"

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Yangi va toza certificates jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course TEXT,
            direction_name TEXT,
            full_name TEXT NOT NULL,
            issued_at TIMESTAMP NOT NULL,
            certificate_path TEXT,
            test_result_id INTEGER UNIQUE
        )
    """)

    # Agar eski jadval bo'lsa ma'lumotlarni ko'chiramiz
    try:
        cursor.execute("SELECT id, user_id, full_name, issued_at FROM certificates")
        rows = cursor.fetchall()
        for r in rows:
            cursor.execute("""
                INSERT OR IGNORE INTO certificates_new (id, user_id, full_name, issued_at)
                VALUES (?, ?, ?, ?)
            """, r)
    except Exception as e:
        print(f"Ko'chirishda ogohlantirish: {e}")

    cursor.execute("DROP TABLE IF EXISTS certificates")
    cursor.execute("ALTER TABLE certificates_new RENAME TO certificates")

    conn.commit()
    conn.close()
    print("Muvaffaqiyatli: certificates jadvali to'liq yangilandi!")
else:
    print("Baza topilmadi.")
