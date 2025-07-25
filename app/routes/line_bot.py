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
    elif "出席" in text:
        reply = get_attendance_by_line_id(line_id)
    elif "公告" in text:
        reply = get_announcements()
    else:
        reply = "請輸入「公告」、「出席」或「綁定 <帳號>」"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

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
            return "⚠️ 請先綁定帳號，例如輸入：綁定 nekorin"

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

def get_announcements():
    url = "https://de0692c0df9b.ngrok-free.app/coach/api/announcements"
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
