from cryptography.fernet import Fernet
import os

# 1. إعداد التشفير
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def encrypt_key(plain_text):
    """تشفير النصوص قبل حفظها"""
    if plain_text:
        return cipher.encrypt(plain_text.encode())
    return None

def decrypt_key(encrypted_text):
    """فك تشفير النصوص عند الحاجة"""
    if encrypted_text:
        try:
            return cipher.decrypt(encrypted_text).decode()
        except Exception as e:
            print(f"❌ خطأ في فك التشفير: {e}")
            return None
    return None

def start_trading_cycle(exchange, session, db, buy_price, amount_to_buy):
    """دالة تنفيذ منطق التداول وجني الأرباح"""
    try:
        # جلب الرصيد وتحديد الهدف (10%)
        balance = exchange.fetch_balance()
        current_usdt = balance['free'].get('USDT', 0)
        target_profit_usd = current_usdt * 0.10 
        
        print(f"💰 رأس المال: {current_usdt}$ | الهدف: {target_profit_usd}$")
        
        while True:
            # جلب السعر الحالي
            ticker = exchange.fetch_ticker(session.symbol)
            current_price = ticker['last']
            
            # حساب الربح اللحظي
            profit_usd = (current_price - buy_price) * amount_to_buy
            session.live_pnl = profit_usd
            db.session.commit()

            # التحقق من الهدف
            if profit_usd >= target_profit_usd:
                print(f"✅ تحقق الهدف! ربح: {profit_usd:.2f}$")
                exchange.create_market_sell_order(session.symbol, amount_to_buy)
                
                session.total_profit_usd += profit_usd
                db.session.commit()
                break 
    except Exception as e:
        print(f"❌ خطأ في حلقة التداول: {e}")
        
