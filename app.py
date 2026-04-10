from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import threading
import secrets
import string
from models import db, TradingSession
from encryptor import encrypt_key, decrypt_key
from engine import start_trading_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# --- 1. دالة التحقق من صلاحية التطبيق (24 ساعة أو تفعيل شهرين) ---
@app.route('/check_access/<user_id>', methods=['GET'])
def check_access(user_id):
    user = TradingSession.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"status": "new_user"})

    time_passed = datetime.utcnow() - user.install_date
    
    # إذا لم يفعل الكود ومرت 24 ساعة (86400 ثانية)
    if not user.is_fully_activated and time_passed.total_seconds() > 86400:
        return jsonify({"status": "expired", "message": "انتهت الفترة التجريبية"})
    
    return jsonify({"status": "access_granted"})

# --- 2. دالة تشغيل البوت (التداول الحقيقي لمدة 12 ساعة) ---
@app.route('/start_bot', methods=['POST'])
def start_bot():
    data = request.json
    user_id = data.get('user_id')
    api_key = data.get('api_key')
    api_secret = data.get('api_secret')
    exchange = data.get('exchange')
    symbol = data.get('symbol', 'BTC/USDT')

    # فحص الصلاحية قبل البدء
    check = check_access(user_id)
    if check.json.get('status') == 'expired':
        return jsonify({"status": "error", "message": "يرجى التفعيل أولاً"}), 403

    # تشفير وحفظ الجلسة
    new_session = TradingSession(
        user_id=user_id, exchange=exchange, symbol=symbol, is_active=True
    )
    db.session.add(new_session)
    db.session.commit()

    # تشغيل المحرك في الخلفية (12 ساعة، هدف 5$)
    thread = threading.Thread(target=start_trading_engine, 
                             args=(app, new_session.id, api_key, api_secret))
    thread.start()

    return jsonify({"status": "success", "message": "🚀 تم بدء التداول لمدة 12 ساعة"})

# --- 3. نظام "موافق" لتوليد رمز تفعيل تلقائي (للأدمن) ---
@app.route('/admin/generate_code', methods=['POST'])
def generate_code():
    # توليد رمز عشوائي 8 رموز
    new_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    # حفظ الكود في ملف مؤقت أو قاعدة البيانات (لأغراض العرض)
    with open("active_codes.txt", "a") as f:
        f.write(f"{new_code}\n")
        
    return jsonify({
        "status": "success", 
        "generated_code": new_code,
        "message": "أعطِ هذا الرمز للمستخدم لتفعيل التطبيق"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  
