# app/routes/coach.py

from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from app.database import get_db
from app.models.announcement import Announcement

coach_bp = Blueprint("coach", __name__, url_prefix="/coach")


@coach_bp.route("/", methods=["GET"])
def dashboard():
    # 教練主控台，只顯示大按鈕（公告管理、點名）
    return render_template("coach/dashboard.html")


@coach_bp.route("/announcements", methods=["GET"])
def announcements():
    # 列出所有公告
    with get_db() as session:
        announcements = (
            session.query(Announcement).order_by(Announcement.date.desc()).all()
        )
    return render_template("coach/announcements.html", announcements=announcements)


@coach_bp.route("/announcements/new", methods=["GET", "POST"])
def new_announcement():
    # 新增公告
    if request.method == "POST":
        form = request.form
        ann = Announcement(
            date=datetime.strptime(form["date"], "%Y-%m-%d").date(),
            title=form["title"],
            content=form["content"],
            category=form["category"],
            coach_id=1,  # TODO: 換成 current_user.id
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


@coach_bp.route("/rollcall", methods=["GET"])
def roll_call():
    return render_template("coach/rollcall.html")
