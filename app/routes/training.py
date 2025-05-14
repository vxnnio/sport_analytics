# routes/training.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import json

from app.models.training import Training
from app.database import get_db

training_bp = Blueprint('training', __name__, url_prefix='/training')

@training_bp.route('/today', methods=['GET'])
@login_required
def training_today():
    selected_date = request.args.get('date')
    current_date = selected_date or datetime.today().strftime('%Y-%m-%d')

    with get_db() as db:
        record = db.query(Training).filter_by(user_id=current_user.id, date=current_date).first()

    return render_template('athlete/upload.html', current_date=current_date, record=record)

@training_bp.route('/today/save', methods=['POST'])
@login_required
def training_today_save():
    date_str = request.form.get('selected_date')

    with get_db() as db:
        record = db.query(Training).filter_by(user_id=current_user.id, date=date_str).first()
        if not record:
            record = Training(user_id=current_user.id, date=date_str)

        # 教練派發完成勾選
        record.coach_physical_done = 'coach_physical_done' in request.form
        record.coach_technical_done = 'coach_technical_done' in request.form

        # 主動體能訓練（含空值處理）
        record.jump_type = request.form.get("jump_type") or None
        jump_count_raw = request.form.get("jump_count")
        record.jump_count = int(jump_count_raw) if jump_count_raw and jump_count_raw.strip().isdigit() else None

        run_distance_raw = request.form.get("run_distance")
        record.run_distance = float(run_distance_raw) if run_distance_raw and run_distance_raw.strip() else None

        run_time_raw = request.form.get("run_time")
        record.run_time = float(run_time_raw) if run_time_raw and run_time_raw.strip() else None

        record.weight_sets = request.form.get("weight_sets") or None
        record.agility_type = request.form.get("agility_type") or None
        record.agility_note = request.form.get("agility_note") or None

        # 主動技巧訓練
        record.technical_title = request.form.get("technical_title") or None
        record.technical_feedback = request.form.get("technical_feedback") or None
        record.technical_completed = request.form.get("technical_completed") == "true"

        # 技巧項目 JSON 組裝
        items = []
        categories = request.form.getlist('category[]')
        topics = request.form.getlist('topic[]')
        durations = request.form.getlist('duration[]')
        focuses = request.form.getlist('focus[]')

        for i in range(len(categories)):
            if topics[i].strip():
                items.append({
                    "category": categories[i],
                    "topic": topics[i],
                    "duration_or_reps": durations[i],
                    "focus": focuses[i]
                })
        record.technical_items = json.dumps(items, ensure_ascii=False)

        db.add(record)
        db.commit()

    flash("✅ 今日訓練已儲存")
    return redirect(url_for('training.training_today', date=date_str))
