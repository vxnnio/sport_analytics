from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import logging
from app.models.evaluation import Evaluation
from app.models.announcement import Announcement
from app.database import get_db

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
    selected_date = request.form.get("selected_date")
    try:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except Exception as e:
        flash("日期格式錯誤", "danger")
        return redirect(url_for("training.training_today"))

    try:
        with get_db() as db:
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
            record.technical_completed = request.form.get("technical_completed") == "on"

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
            else:
                record.technical_items = None

            record.coach_physical_done = request.form.get("coach_physical_done") == "on"
            record.coach_technical_done = request.form.get("coach_technical_done") == "on"

            db.add(record)
            db.commit()

        flash("今日訓練已成功儲存", "success")

    except Exception as e:
        logging.error(f"儲存錯誤，日期: {selected_date}, 用戶ID: {current_user.id}, 錯誤: {e}")
        flash(f"儲存錯誤：{e}", "danger")
    return redirect(url_for("auth.dashboard"))

@training_bp.route('/view', methods=['GET'])
@login_required
def view_training_records():
    """
    學生查看自己所有上傳的訓練資料（歷史紀錄）
    可選擇日期查詢
    """
    selected_date = request.args.get('date')  # 可選擇日期
    with get_db() as db:
        query = db.query(Training).filter_by(user_id=current_user.id).order_by(Training.date.desc())
        
        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
                query = query.filter_by(date=date_obj)
            except Exception as e:
                flash("日期格式錯誤", "danger")

        records = query.all()

    return render_template('athlete/view_records.html', records=records, selected_date=selected_date)


@training_bp.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_training_record(record_id):
    with get_db() as db:
        record = db.query(Training).filter_by(id=record_id, user_id=current_user.id).first()
        if not record:
            flash("找不到紀錄或沒有權限刪除", "danger")
            return redirect(url_for('training.view_training_records'))

        db.delete(record)
        db.commit()

    flash("紀錄已刪除", "success")
    return redirect(url_for('training.view_training_records'))
