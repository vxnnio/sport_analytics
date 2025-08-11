from flask import Blueprint, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 從環境變數讀取 API KEY

chat_bp = Blueprint('chat', __name__, url_prefix="/chatbot")

@chat_bp.route('/')
def index():
    return render_template('athlete/chatbot.html')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    user_message = data.get('message', '')

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一位桌球教練，請用簡單中文回答"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = completion.choices[0].message.content
        return jsonify({'reply': reply})

    except Exception as e:
        # 印出錯誤，方便除錯
        print(f"Error in chat API: {e}")
        return jsonify({'reply': '伺服器發生錯誤，請稍後再試。'}), 500
