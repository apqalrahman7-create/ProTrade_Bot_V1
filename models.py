from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TradingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    exchange = db.Column(db.String(20))      # اسم المنصة (مثل Binance)
    symbol = db.Column(db.String(10))        # زوج التداول (مثل BTC/USDT)
    
    # --- بيانات المحفظة الحقيقية ---
    initial_balance = db.Column(db.Float)    # الرصيد عند بداية تشغيل البوت
    current_balance = db.Column(db.Float)    # الرصيد الحالي المتاح للتداول
    
    # --- بيانات الصفقة الحالية (إعادة الاستثمار) ---
    last_entry_price = db.Column(db.Float)   # السعر الذي اشترى به البوت في آخر دورة
    amount_held = db.Column(db.Float)        # كمية العملات التي يمتلكها البوت حالياً
    
    # --- البيانات التي تظهر في شاشة التطبيق ---
    total_profit_usd = db.Column(db.Float, default=0.0) # مجموع الأرباح المحققة (تراكم الـ 5$)
    live_pnl = db.Column(db.Float, default=0.0)         # الربح اللحظي المباشر بالدولار
    
    # --- التوقيت والحالة ---
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)     # هل البوت يعمل (مدة الـ 12 ساعة)
