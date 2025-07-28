# app/routes/stress_evaluate.py

import traceback
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.database import get_db
from app.models.stress_evaluate import StressEvaluate

# ✅ 修正：補上 template_folder，讓 Flask 正確尋找 HTML 模板
stress_bp = Blueprint('stress_evaluate', __name__, url_prefix='/stress', template_folder='../templates')

@stress_bp.route("/evaluate", methods=["GET"])
@login_required
def show_form():
    return render_template("athlete/stress_evaluate.html")

@stress_bp.route("/evaluate", methods=["POST"])
@login_required
def submit_form():
    try:
        data = {f"q{i}": int(request.form.get(f"q{i}", 0)) for i in range(1, 18)}
        total_score = sum(data.values())

        if total_score < 25:
            result = "壓力狀況良好"
        elif total_score < 45:
            result = "中度壓力，建議多休息與自我調適"
        else:
            result = "高壓狀態，請考慮尋求專業協助"

        new_record = StressEvaluate(athlete_id=current_user.id, **data)
        with get_db() as db:
            db.add(new_record)
            db.commit()

        return render_template("athlete/stress_result.html", total_score=total_score, result=result)

    except Exception as e:
        print("錯誤發生：", e)
        traceback.print_exc()
        return "提交過程中發生錯誤，請稍後再試。", 500


