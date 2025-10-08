from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging
from app.models.evaluation import Evaluation
from app.database import get_db, SessionLocal

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

# 顯示評估表單（可選日期）
@evaluation_bp.route('/form', methods=['GET'])
@login_required
def evaluation_form():
    # 從 query string 拿日期，沒傳就用今天
    current_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    try:
        date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()
    except ValueError:
        flash("日期格式錯誤", "danger")
        date_obj = datetime.today().date()
        current_date = date_obj.strftime('%Y-%m-%d')

    with get_db() as db:
        record = db.query(Evaluation).filter_by(user_id=current_user.id, eval_date=date_obj).first()

    return render_template(
        "athlete/evaluation_form.html",
        current_date=current_date,
        record=record,
        zip=zip,
        getattr=getattr
    )

# 儲存/更新評估
@evaluation_bp.route('/save', methods=['POST'])
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

            # 儲存評分欄位
            record.training_status = int(request.form.get("training_status") or 0)
            record.fitness = int(request.form.get("fitness") or 0)
            record.sleep = int(request.form.get("sleep") or 0)
            record.appetite = int(request.form.get("appetite") or 0)
            record.note = request.form.get("note") or ""

            db.add(record)
            db.commit()

        flash("評估已成功儲存", "success")
    except Exception as e:
        logging.error(f"儲存錯誤：{e}")
        flash(f"儲存錯誤：{e}", "danger")

    return redirect(url_for("evaluation.view_evaluation_records"))

# 查看所有評估紀錄
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

    # 將資料轉成前端方便使用的格式
    records_data = [
        {
            "eval_date_str": r.eval_date.strftime("%Y-%m-%d"),
            "training_status": r.training_status or 0,
            "fitness": r.fitness or 0,
            "sleep": r.sleep or 0,
            "appetite": r.appetite or 0,
            "note": r.note or ""
        }
        for r in records
    ]

    return render_template(
        "athlete/view_evaluations.html",
        records=records,
        records_data=records_data
    )

# JSON API 給折線圖
@evaluation_bp.route('/chart_data', methods=['GET'])
@login_required
def evaluation_chart_data():
    with get_db() as db:
        records = db.query(Evaluation).filter_by(user_id=current_user.id).order_by(Evaluation.eval_date.asc()).all()
        data = {
            "dates": [r.eval_date.strftime("%Y-%m-%d") for r in records],
            "training_status": [r.training_status or 0 for r in records],
            "fitness": [r.fitness or 0 for r in records],
            "sleep": [r.sleep or 0 for r in records],
            "appetite": [r.appetite or 0 for r in records]
        }
    return jsonify(data)
