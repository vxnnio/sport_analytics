from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging
from app.models.evaluation import Evaluation
from app.database import get_db
from sqlalchemy.orm import Session
from app.database import SessionLocal

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

# 顯示今日評估表單
@evaluation_bp.route('/form', methods=['GET'])
@login_required
def evaluation_form():
    current_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()

    with get_db() as db:
        record = db.query(Evaluation).filter_by(user_id=current_user.id, eval_date=date_obj).first()

    return render_template("athlete/evaluation_form.html", current_date=current_date, record=record,zip=zip,getattr=getattr)

# 儲存今日評估
@evaluation_bp.route('/today/save', methods=['POST'])
@login_required
def save_evaluation():
    selected_date = request.form.get("selected_date")
    try:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except Exception:
        flash("日期格式錯誤", "danger")
        return redirect(url_for("evaluation.evaluation_form"))

    try:
        with get_db() as db:
            record = db.query(Evaluation).filter_by(user_id=current_user.id, eval_date=date_obj).first()
            if not record:
                record = Evaluation(user_id=current_user.id, eval_date=date_obj)

            # 直接存整數 1~5
            record.training_status = int(request.form.get("training_status"))
            record.fitness = int(request.form.get("fitness"))
            record.sleep = int(request.form.get("sleep"))
            record.appetite = int(request.form.get("appetite"))
            record.note = request.form.get("note")

            db.add(record)
            db.commit()

        flash("今日評估已成功儲存", "success")
    except Exception as e:
        logging.error(f"儲存錯誤：{e}")
        flash(f"儲存錯誤：{e}", "danger")

    return redirect(url_for("evaluation.view_evaluation_records"))

@evaluation_bp.route("/view", methods=["GET"])
@login_required
def view_evaluation_records():
    db = SessionLocal()
    athlete_id = current_user.id  

    records = (
        db.query(Evaluation)
        .filter(Evaluation.user_id == athlete_id)
        .order_by(Evaluation.eval_date)
        .all()
    )

    # ✅ 在這裡加工成 dict，避免 Jinja2 取不到欄位
    records_data = []
    for r in records:
        records_data.append({
            "eval_date_str": r.eval_date.strftime("%Y-%m-%d"),
            "training_status": r.training_status or 0,
            "fitness": r.fitness or 0,
            "sleep": r.sleep or 0,
            "appetite": r.appetite or 0,
            "note": r.note or ""
        })

    return render_template(
        "athlete/view_evaluations.html",
        records=records,          # 如果模板還要用完整物件，這個保留
        records_data=records_data # ✅ 給 Chart.js 用乾淨的 JSON 資料
    )

# JSON API 給折線圖
@evaluation_bp.route('/chart_data', methods=['GET'])
@login_required
def evaluation_chart_data():
    with get_db() as db:
        records = db.query(Evaluation).filter_by(user_id=current_user.id).order_by(Evaluation.eval_date.asc()).all()
        data = {
            "dates": [r.eval_date.strftime("%Y-%m-%d") for r in records],
            "training_status": [r.training_status for r in records],
            "fitness": [r.fitness for r in records],
            "sleep": [r.sleep for r in records],
            "appetite": [r.appetite for r in records]
        }
    return jsonify(data)


# evaluation.py
def get_records_from_db(db, athlete_id):
    records = (
        db.query(Evaluation)
        .filter(Evaluation.user_id == athlete_id)
        .order_by(Evaluation.eval_date)
        .all()
    )

    for r in records:
        # 日期轉字串
        r.eval_date_str = r.eval_date.strftime('%Y-%m-%d') if r.eval_date else ""
        # 分數欄位確保不是 None
        r.score1 = r.score1 if r.score1 is not None else 0
        r.score2 = r.score2 if r.score2 is not None else 0
        r.score3 = r.score3 if r.score3 is not None else 0

    return records

