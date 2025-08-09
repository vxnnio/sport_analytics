from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os
from dotenv import load_dotenv
from app.database import get_db
from app.models.user import User
from app.models.attendance import Attendance
from linebot.models import FlexSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

# 啟用排程器（全域）
scheduler = BackgroundScheduler(timezone="Asia/Taipei")

def send_evaluation_card_to_all_users():
    with get_db() as session:
        users = session.query(User).filter(User.line_user_id.isnot(None)).all()

    for user in users:
        try:
            message = get_evaluation_card()
            line_bot_api.push_message(user.line_user_id, message)
            print(f"[{datetime.now()}] 推播評估卡片給 {user.username}")
        except Exception as e:
            print(f"推播給 {user.username} 時出錯: {str(e)}")

# 設定每天上午 9 點自動推播
scheduler.add_job(send_evaluation_card_to_all_users, 'cron', hour=12, minute=30)

# 啟動排程器（放在 create_app() 的地方會更安全）
scheduler.start()

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = 'N3vgXKPPqJYif6rTleXpxpvt05mvfxopvm9nO4VHinEuLwXIjLLenmQylu+vyaDmzyUlU8Jo/ANx0TgwQxoc+9NXAnUlaIWayeMV+6MZYxlaeVfUbMnnYiPMx+fzQ+zyKH8TORI1vN3A1QOu4eYZXQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '10f47ad2b6acfdbc1c3c3a602974ac2f'

line_bp = Blueprint("line", __name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@line_bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    print("Received body:", body)
    print("Signature:", signature)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip().lower()
    line_id = event.source.user_id

    if text.startswith("綁定"):
        username = text.replace("綁定", "").strip()
        reply = bind_account(username, line_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        
    elif text.startswith("綁定狀態"):
        user = get_user_by_line_id(line_id)
        if user:
            reply = f"您已綁定帳號：{user.username}"
        else:
            reply = "您尚未綁定帳號，請輸入：綁定 <帳號>"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    elif "出席" in text:
        reply = get_attendance_by_line_id(line_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    elif "公告" in text:
        reply = get_announcements()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    elif "評估表" in text:
        flex_message = get_evaluation_card()
        line_bot_api.reply_message(event.reply_token, flex_message)

    else:
        reply = "請輸入「公告」、「出席」、「評估表」或「綁定 <帳號>」"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

def bind_account(username, line_id):
    with get_db() as session:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return "❌ 找不到該帳號"
        user.line_user_id = line_id
        session.commit()
        return f"✅ 成功綁定帳號 {username}"

def get_attendance_by_line_id(line_id):
    with get_db() as session:
        user = session.query(User).filter_by(line_user_id=line_id).first()
        if not user:
            print("❌ LINE 使用者尚未綁定")
            return "您尚未綁定帳號，請輸入：綁定 <帳號>"
        else:
            print(f"✅ 使用者已綁定：{user.username} (ID: {user.id})")
            
        records = (
            session.query(Attendance)
            .filter_by(athlete_id=user.id)
            .order_by(Attendance.date.desc())
            .limit(5)
            .all()
        )

        if not records:
            return "📭 尚無出缺席紀錄"

        status_map = {
            "present": "✅ 出席",
            "absent": "❌ 缺席",
            "late": "⏰ 遲到",
            "leave": "📌 請假"
        }

        msg = f"📋 {user.username} 的最近出缺席紀錄：\n"
        for r in records:
            zh_status = status_map.get(r.status.lower(), r.status)
            date_str = r.date.strftime("%Y/%m/%d")
            msg += f"📅 {date_str}：{zh_status}\n"

        return msg
        return msg

def get_user_by_line_id(line_id):
    with get_db() as session:
        user = session.query(User).filter_by(line_user_id=line_id).first()
        return user


def get_announcements():
    url = "https://14edbb0818c2.ngrok-free.app/coach/api/announcements"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if not data:
                return "目前沒有公告"
            msg = "📢 最新公告：\n"
            for a in data[:3]:
                msg += f"\n🔸 {a['title']}（{a['created_at']}）\n{a['content']}\n"
            return msg
        else:
            return "無法取得公告"
    except Exception as e:
        return f"錯誤：{str(e)}"

def get_evaluation_card():
    flex_content = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip1.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "填寫訓練評估表",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "請填寫最近的訓練評估紀錄",
                    "size": "sm",
                    "color": "#999999",
                    "margin": "md",
                    "align": "center"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "uri",
                        "label": "前往填寫",
                        "uri": "https://14edbb0818c2.ngrok-free.app/evaluation/form"
                    }
                }
            ]
        }
    }

    return FlexSendMessage(alt_text="請填寫訓練評估表", contents=flex_content)
