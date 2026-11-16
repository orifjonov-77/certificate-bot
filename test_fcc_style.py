import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import certificate_maker

def test():
    print("PDF uslubidagi yangi sertifikatni sinovdan o'tkazish...")
    path = certificate_maker.make_certificate(
        full_name="Xulkaroy Soliyeva",
        course="Excel",
        score=19,
        cert_id=1,
        user_id=123456789
    )
    print(f"Sertifikat tayyor: {path}")

if __name__ == "__main__":
    test()
