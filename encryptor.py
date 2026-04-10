from cryptography.fernet import Fernet
import os

# توليد مفتاح تشفير فريد للمشروع
# ملاحظة: في النسخة النهائية، يجب حفظ هذا المفتاح في ملف .env وعدم تغييره أبداً
# لكي لا تفقد القدرة على فك تشفير المفاتيح القديمة.
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def encrypt_key(plain_text):
    """تشفير النصوص (مثل API Key) قبل حفظها في قاعدة البيانات"""
    if plain_text:
        return cipher.encrypt(plain_text.encode())
    return None

def decrypt_key(encrypted_text):
    """فك تشفير النصوص عند الحاجة لاستخدامها في محرك التداول"""
    if encrypted_text:
        try:
            return cipher.decrypt(encrypted_text).decode()
        except Exception as e:
            print(f"❌ خطأ في فك التشفير: {e}")
            return None
    return None
  
