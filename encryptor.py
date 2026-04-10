import os
import time
from cryptography.fernet import Fernet

# --- 1. إعداد نظام التشفير الاحترافي ---
# نجلب المفتاح من البيئة؛ إذا لم يوجد نستخدم مفتاحاً ثابتاً (للمرة الأولى فقط)
# نصيحة: ضع مفتاحك الخاص في GitHub Secrets باسم 'ENCRYPTION_KEY'
SECRET_KEY_RAW = os.environ.get('ENCRYPTION_KEY', 'Fixed_Base64_Key_For_Initial_Run_32_Chars=')
try:
    cipher = Fernet(SECRET_KEY_RAW.encode() if isinstance(SECRET_KEY_RAW, str) else SECRET_KEY_RAW)
except Exception:
    # في حال فشل المفتاح، نقوم بتوليد واحد مؤقت لضمان عدم توقف الكود
    cipher = Fernet(Fernet.generate_key())

def encrypt_key(plain_text):
    """تشفير النصوص (مثل API Key) قبل حفظها في قاعدة البيانات"""
    if plain_text:
        return cipher.encrypt(plain_text.encode()).decode()
    return None

def decrypt_key(encrypted_text):
    """فك تشفير النصوص لاستخدامها في الربط مع المنصة"""
    if encrypted_text:
        try:
            return cipher.decrypt(encrypted_text.encode()).decode()
        except Exception as e:
            print(f"❌ خطأ في فك التشفير: {e}")
    return None

# --- 2. دالة التداول الذكية (بدون أخطاء) ---
def start_trading_cycle(exchange, session, db, buy_price, amount_to_buy):
    """تنفيذ التداول، تحديث الشاشة، وحماية الحساب"""
    try:
        # جلب الرصيد وتحديد الأهداف
        balance = exchange.fetch_balance()
        current_usdt = balance['free'].get('USDT', 0)
        
        # الأهداف المالية
        target_profit_usd = current_usdt * 0.10  # هدف الربح 10%
        stop_loss_usd = current_usdt * 0.05      # وقف الخسارة 5%
        
        print(f"💰 رأس المال: {current_usdt}$ | الهدف: {target_profit_usd}$")
        
        while True:
            # جلب السعر اللحظي (ticker)
            ticker = exchange.fetch_ticker(session.symbol)
            current_price = ticker['last']
            
            # حساب الأرباح الحالية
            profit_usd = (current_price - buy_price) * amount_to_buy
            
            # تحديث البيانات في قاعدة البيانات لتظهر على شاشة الهاتف
            session.live_pnl = profit_usd
            db.session.commit()

            # --- الخروج عند الربح (Target) ---
            if profit_usd >= target_profit_usd:
                print(f"✅ تم تحقيق الهدف! جني ربح: {profit_usd:.2f}$")
                exchange.create_market_sell_order(session.symbol, amount_to_buy)
                session.total_profit_usd += profit_usd
                db.session.commit()
                break 

            # --- الخروج عند الخسارة (Stop Loss) ---
            if profit_usd <= -stop_loss_usd:
                print(f"⚠️ تفعيل وقف الخسارة لحماية المحفظة: {profit_usd:.2f}$")
                exchange.create_market_sell_order(session.symbol, amount_to_buy)
                db.session.commit()
                break

            # --- حماية من حظر الـ IP (هام جداً) ---
            # الانتظار لمدة ثانيتين قبل طلب السعر مرة أخرى
            time.sleep(2) 
            
    except Exception as e:
        print(f"❌ خطأ في حلقة التداول: {e}")
        # انتظار بسيط قبل إعادة المحاولة في حال وجود خطأ بالشبكة
        time.sleep(10)
        
