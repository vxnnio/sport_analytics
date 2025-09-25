# app/routes/athlete.py

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.database import get_db
from app.models.attendance import Attendance
from app.models import SleepRecord
from datetime import datetime, timedelta

athlete_bp = Blueprint("athlete", __name__, url_prefix="/athlete")

@athlete_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("athlete/dashboard.html")

@athlete_bp.route("/attendance", methods=["GET"])
@login_required
def view_attendance():
    with get_db() as session:
        records = (
            session.query(Attendance)
            .filter_by(athlete_id=current_user.id)
            .order_by(Attendance.date.desc())
            .all()
        )
    return render_template("athlete/attendance.html", attendance_records=records)

@athlete_bp.route("/api/attendance/<int:athlete_id>", methods=["GET"])
def api_attendance(athlete_id):
    with get_db() as session:
        records = (
            session.query(Attendance)
            .filter_by(athlete_id=athlete_id)
            .order_by(Attendance.date.desc())
            .all()
        )
        result = [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "status": r.status
            }
            for r in records
        ]
        return jsonify(result)

@athlete_bp.route('/sleep_record', methods=['GET', 'POST'])
@login_required
def sleep_record():
    if current_user.role != 'athlete':
        flash("只有選手可以使用此功能", "danger")
        return redirect(url_for('main.index'))

    with get_db() as db:
        # 新增紀錄
        if request.method == 'POST':
            record_date = request.form['record_date']
            sleep_start = request.form['sleep_start']
            sleep_end = request.form['sleep_end']

            # 防止重複新增
            existing = db.query(SleepRecord).filter_by(
                athlete_id=current_user.id,
                record_date=record_date
            ).first()
            if existing:
                flash("你已經填過該日期的睡眠紀錄", "warning")
            else:
                record = SleepRecord(
                    athlete_id=current_user.id,
                    record_date=record_date,
                    sleep_start=sleep_start,
                    sleep_end=sleep_end,
                    created_by=current_user.id
                )
                db.add(record)
                db.commit()
                flash("睡眠紀錄已新增", "success")

            return redirect(url_for('athlete.sleep_record'))

        # 查詢自己的紀錄
        records = db.query(SleepRecord).filter_by(
            athlete_id=current_user.id
        ).order_by(SleepRecord.record_date.desc()).all()

        # 計算睡眠時長
        for r in records:
            try:
                # r.sleep_start 和 r.sleep_end 已經是 datetime.time
                start_dt = datetime.combine(r.record_date, r.sleep_start)
                end_dt = datetime.combine(r.record_date, r.sleep_end)

                # 跨日處理：睡到隔天
                if end_dt <= start_dt:
                    end_dt += timedelta(days=1)

                # 計算睡眠時長
                r.sleep_duration = end_dt - start_dt  # datetime.timedelta
            except Exception as e:
                r.sleep_duration = None
                print(f"睡眠計算錯誤：{e}")

    return render_template('athlete/sleep_record.html', records=records)


