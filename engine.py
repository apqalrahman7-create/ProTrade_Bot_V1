import ccxt
import time
from datetime import datetime, timedelta
from models import db, TradingSession

def start_trading_engine(app, session_id, api_key, api_secret):
    with app.app_context():
        # 1. جلب بيانات الجلسة من القاعدة
        session = TradingSession.query.get(session_id)
        if not session: return

        try:
            # 2. الاتصال بالمنصة الحقيقية
            exchange_class = getattr(ccxt, session.exchange)
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })

            # تحديد وقت التوقف التلقائي (بعد 12 ساعة)
            stop_time = datetime.utcnow() + timedelta(hours=12)

            while datetime.utcnow() < stop_time and session.is_active:
                # --- أ. جلب الرصيد الحقيقي وتحديثه في التطبيق ---
                balance = exchange.fetch_balance()
                current_usdt = balance['free'].get('USDT', 0)
                session.current_balance = current_usdt
                db.session.commit()

                if current_usdt < 10: # توقف إذا كان الرصيد غير كافٍ
                    print("⚠️ الرصيد منخفض جداً للتداول.")
                    break

                # --- ب. تنفيذ عملية شراء (إعادة استثمار الرصيد بالكامل) ---
                ticker = exchange.fetch_ticker(session.symbol)
                buy_price = ticker['last']
                amount_to_buy = current_usdt / buy_price
                
                print(f"🚀 شراء {session.symbol} بسعر {buy_price}")
                exchange.create_market_buy_order(session.symbol, amount_to_buy)
                
                session.last_entry_price = buy_price
                db.session.commit()

                # --- ج. مراقبة الصفقة حتى تحقيق ربح 5 دولار ---
                while True:
                    # تحديث السعر والربح اللحظي (Live PnL) ليعرض في التطبيق
                    current_ticker = exchange.fetch_ticker(session.symbol)
                    current_price = current_ticker['last']
                    
                    # حساب الربح بالدولار
                    profit_usd = (current_price - buy_price) * amount_to_buy
                    session.live_pnl = profit_usd
                    db.session.commit()

                    # التحقق من هدف الربح (5 دولار)
                    if profit_usd >= 5.0:
                        print(f"💰 تم تحقيق ربح {profit_usd:.2f}$ | جاري البيع وإعادة الاستثمار...")
                        exchange.create_market_sell_order(session.symbol, amount_to_buy)
                        
                        # إضافة الربح للإجمالي وتحديث الرصيد
                        session.total_profit_usd += profit_usd
                        db.session.commit()
                        break # العودة لبداية الحلقة لبدء صفقة جديدة بالرصيد الجديد

                    # التوقف إذا انتهت الـ 12 ساعة أثناء مراقبة الصفقة
                    if datetime.utcnow() > stop_time:
                        exchange.create_market_sell_order(session.symbol, amount_to_buy)
                        break

                    time.sleep(10) # فحص السعر كل 10 ثوانٍ لسرعة التحديث

        except Exception as e:
            print(f"❌ خطأ في المحرك الحقيقي: {e}")
        finally:
            session.is_active = False
            db.session.commit()
            print("🏁 انتهت مدة العمل (12 ساعة) وتم إغلاق كافة العمليات.")
          
