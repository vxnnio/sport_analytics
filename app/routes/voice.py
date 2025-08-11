from flask import Blueprint, request, jsonify, render_template

voice_bp = Blueprint('voice', __name__, url_prefix="/voicebot")

@voice_bp.route('/')
def index():
    return render_template('athlete/voicebot.html')

@voice_bp.route('/voice', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower()  # 小寫比較方便關鍵字比對

    # 關鍵字教學對應
    if "發球" in user_message:
        reply = "發球時，球必須平放在手掌上拋起，拋高不少於16公分，並在落下時擊球。"
    elif "旋轉" in user_message:
        reply = "旋轉球分為上旋、下旋、側旋，會影響球的彈跳和飛行方向。"
    elif "接球" in user_message or "接發球" in user_message:
        reply = "接球時應提前預判對手的旋轉與落點，身體保持低姿態迎接來球。"
    elif "殺球" in user_message:
        reply = "殺球是一種快速進攻技術，通常在對方回球過高時使用，速度快、角度刁。"
    elif "反手" in user_message:
        reply = "反手擊球是指用拍面背面來擊球，常用於處理右側來球。"
    else:
        reply = f"你說了：{user_message}，我還在學習這方面的內容喔～"

    return jsonify({'reply': reply})
