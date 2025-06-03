# app/routes/coach.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask import flash
from datetime import datetime
from app.database import get_db
from app.models.announcement import Announcement
from app.models.user import User  
from app.models.attendance import Attendance
from flask_login import login_required
from flask_login import current_user
from app.database import SessionLocal



coach_bp = Blueprint("coach", __name__, url_prefix="/coach")


@coach_bp.route("/", methods=["GET"])
def dashboard():
    # 教練主控台，只顯示大按鈕（公告管理、點名）
    return render_template("coach/dashboard.html")


@coach_bp.route("/announcements", methods=["GET"])
@login_required
def announcements():
    # 创建会话
    session = SessionLocal()

    try:
        # 使用 session.query() 进行查询
        announcements = (
            session.query(Announcement)
            .filter(Announcement.coach_id == current_user.id)
            .order_by(Announcement.date.desc())  # 按日期降序排序
            .all()
        )

        # 渲染模板并返回
        return render_template("coach/announcements.html", announcements=announcements)

    finally:
        session.close()  # 确保关闭会话
@coach_bp.route("/announcements/new", methods=["GET", "POST"])
@login_required
def new_announcement():
    if request.method == "POST":
        form = request.form
        ann = Announcement(
            date=datetime.strptime(form["date"], "%Y-%m-%d").date(),
            title=form["title"],
            content=form["content"],
            category=form["category"],
            coach_id=current_user.id,  # ✅ 改這裡
        )
        with get_db() as session:
            session.add(ann)
            session.commit()
        return redirect(url_for("coach.announcements"))

    return render_template("coach/new_announcement.html")

@coach_bp.route("/announcements/<int:aid>/edit", methods=["GET", "POST"])
def edit_announcement(aid):
    # 編輯公告
    with get_db() as session:
        ann = session.query(Announcement).get(aid)
        if not ann:
            return "Not Found", 404

        if request.method == "POST":
            form = request.form
            ann.date = datetime.strptime(form["date"], "%Y-%m-%d").date()
            ann.title = form["title"]
            ann.content = form["content"]
            ann.category = form["category"]
            session.commit()
            return redirect(url_for("coach.announcements"))

    return render_template("coach/edit_announcement.html", announcement=ann)


@coach_bp.route("/announcements/<int:aid>/delete", methods=["POST"])
def delete_announcement(aid):
    # 刪除公告
    with get_db() as session:
        ann = session.query(Announcement).get(aid)
        if not ann:
            return "Not Found", 404
        session.delete(ann)
        session.commit()

    return redirect(url_for("coach.announcements"))



@coach_bp.route("/rollcall", methods=["GET", "POST"])
@login_required
def roll_call():
    with get_db() as session:
        athletes = session.query(User).filter_by(role='athlete').all()
        
        if request.method == "POST":
            roll_date_str = request.form.get("roll_date")
            roll_date = datetime.strptime(roll_date_str, "%Y-%m-%d").date()

            for athlete in athletes:
                status = request.form.get(f"attendance_{athlete.id}")
                if status:
                    # 檢查是否已存在該選手在該日期的點名紀錄，避免重複
                    existing = session.query(Attendance).filter_by(
                        athlete_id=athlete.id, date=roll_date
                    ).first()
                    
                    if existing:
                        existing.status = status  # 更新原紀錄
                    else:
                        attendance = Attendance(
                            athlete_id=athlete.id,
                            date=roll_date,
                            status=status
                        )
                        session.add(attendance)

            session.commit()
            flash("✅ 點名結果已成功儲存！", "success")
            return redirect(url_for("coach.roll_call"))

        today = datetime.today().strftime("%Y-%m-%d")
        return render_template(
            "coach/rollcall.html",
            athletes=athletes,
            today=today
        )

