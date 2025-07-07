from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

# 載入機密參數（.env 方式）
from dotenv import load_dotenv
load_dotenv()

# 替換成你從 LINE Developers 拿到的資料
LINE_CHANNEL_ACCESS_TOKEN = 'N3vgXKPPqJYif6rTleXpxpvt05mvfxopvm9nO4VHinEuLwXIjLLenmQylu+vyaDmzyUlU8Jo/ANx0TgwQxoc+9NXAnUlaIWayeMV+6MZYxlaeVfUbMnnYiPMx+fzQ+zyKH8TORI1vN3A1QOu4eYZXQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '10f47ad2b6acfdbc1c3c3a602974ac2f'

line_bp = Blueprint("line", __name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@line_bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.lower()

    if "公告" in user_text:
        reply = get_announcements()
    else:
        reply = "請輸入「公告」以查看最新公告"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

def get_announcements():
    url = "https://8d9e-1-160-104-101.ngrok-free.app/coach/api/announcements"
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
