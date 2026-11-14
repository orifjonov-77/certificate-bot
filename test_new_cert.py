import asyncio
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import certificate_maker

def test_gen():
    print("Yangi sertifikat dizaynini tekshirish...")
    path = certificate_maker.make_certificate(
        full_name="Orifjonov Muhammadsodiq",
        course="HTML va CSS",
        score=19,
        cert_id=2,
        user_id=8651496098
    )
    print(f"Sertifikat muvaffaqiyatli yaratildi: {path}")

if __name__ == "__main__":
    test_gen()
