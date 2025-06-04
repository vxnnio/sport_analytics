# routes/training.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import json

from app.models.training import Training
from datetime import datetime
from app.models.evaluation import Evaluation # ✅ 新增這行
from app.models.announcement import Announcement
from app.database import get_db  # 引入 get_db
from app.database import SessionLocal
import json

training_bp = Blueprint('training', __name__, url_prefix='/training')

@training_bp.route('/today', methods=['GET'])
@login_required
def training_today():
    selected_date = request.args.get('date')
    current_date = selected_date or datetime.today().strftime('%Y-%m-%d')
    date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()

    with get_db() as db:
        record = db.query(Training).filter_by(user_id=current_user.id, date=date_obj).first()

    return render_template('athlete/upload.html', current_date=current_date, record=record)


@training_bp.route('/today/save', methods=['POST'])
@login_required
def save_today_training():
    db = SessionLocal()

    try:
        selected_date = request.form.get("selected_date")
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

        record = db.query(Training).filter_by(user_id=current_user.id, date=date_obj).first()

        if not record:
            record = Training(user_id=current_user.id, date=date_obj)

        record.jump_type = request.form.get("jump_type")
        record.jump_count = request.form.get("jump_count")
        record.run_distance = request.form.get("run_distance")
        record.run_time = request.form.get("run_time")
        record.weight_sets = request.form.get("weight_sets")
        record.agility_type = request.form.get("agility_type")
        record.agility_note = request.form.get("agility_note")
        
        record.technical_title = request.form.get("technical_title") or record.technical_title
        record.technical_feedback = request.form.get("technical_feedback") or record.technical_feedback
        record.technical_completed = request.form.get("technical_completed") == "true"

        categories = request.form.getlist("category[]")
        topics = request.form.getlist("topic[]")
        durations = request.form.getlist("duration[]")
        focuses = request.form.getlist("focus[]")

        technical_items = []
        for cat, top, dur, foc in zip(categories, topics, durations, focuses):
            if top.strip():
                technical_items.append({
                    "category": cat,
                    "topic": top,
                    "duration_or_reps": dur,
                    "focus": foc
                })
        if technical_items:
            record.technical_items = json.dumps(technical_items)

        record.coach_physical_done = request.form.get("coach_physical_done") == "on"
        record.coach_technical_done = request.form.get("coach_technical_done") == "on"

        db.add(record)
        db.commit()
        flash("今日訓練已成功儲存", "success")

    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"儲存錯誤，日期: {selected_date}, 用戶ID: {current_user.id}, 錯誤: {e}")
        flash(f"儲存錯誤：{e}", "danger")

    finally:
        db.close()

    return redirect(url_for("training.training_today", date=selected_date))


# Jinja2 filter 註冊
import json
@training_bp.app_template_filter('from_json')
def from_json(value):
    if value:
        return json.loads(value)
    return []




