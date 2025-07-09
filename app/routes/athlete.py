# app/routes/athlete.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.database import get_db
from app.models.attendance import Attendance
from flask import jsonify

athlete_bp = Blueprint("athlete", __name__, url_prefix="/athlete")

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



