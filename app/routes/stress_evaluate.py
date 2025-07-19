# app/routes/stress_evaluate.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.database import get_db
from app.models.stress_evaluate import StressEvaluate

stress_bp = Blueprint('stress_evaluate', __name__, url_prefix='/stress')

# 顯示壓力評估表單頁面
@stress_bp.route("/evaluate", methods=["GET"])
@login_required
def show_form():
    return render_template("athlete/stress_evaluate.html")

# 接收表單資料並儲存
@stress_bp.route("/evaluate", methods=["POST"])
@login_required
def submit_form():
    try:
        # 取得 17 題答案
        data = {f"q{i}": request.form.get(f"q{i}") for i in range(1, 18)}
        
        # 建立紀錄物件
        new_record = StressEvaluate(
            athlete_id=current_user.id,
            **{f"q{i}": int(data[f"q{i}"]) for i in range(1, 18)}
        )

        # 寫入資料庫
        with get_db() as db:
            db.add(new_record)
            db.commit()

        return redirect(url_for("athlete.dashboard"))

    except Exception as e:
        print("錯誤發生：", e)
        return "提交過程中發生錯誤，請稍後再試。", 500
