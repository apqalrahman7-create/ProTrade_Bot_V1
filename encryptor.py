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
                  # --- جلب الرصيد الحالي وتحديد الهدف تلقائياً (نسبة 10%) ---
                balance = exchange.fetch_balance()
                current_usdt = balance['free'].get('USDT', 0)
                
                # حساب الهدف: إذا كان الرصيد 50$ يكون الهدف 5$ ، إذا كان 300$ يكون الهدف 30$
                # المعادلة: الربح المستهدف = رأس المال الحالي × 0.10
                target_profit_usd = current_usdt * 0.10 
                
                print(f"💰 رأس المال: {current_usdt}$ | الهدف القادم: {target_profit_usd}$")
                
                # --- تنفيذ الشراء وحساب الربح اللحظي بناءً على الهدف الجديد ---
                while True:
                    # (كود جلب السعر الحالي...)
                    profit_usd = (current_price - buy_price) * amount_to_buy
                    session.live_pnl = profit_usd
                    db.session.commit()

                    # التحقق من الوصول للهدف النسبي (10%)
                    if profit_usd >= target_profit_usd:
                        print(f"✅ تحقق الهدف النسبي! ربح: {profit_usd:.2f}$")
                        exchange.create_market_sell_order(session.symbol, amount_to_buy)
                        
                        session.total_profit_usd += profit_usd
                        db.session.commit()
                        break 
                        
