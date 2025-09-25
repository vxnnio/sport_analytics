from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Training,SleepRecord,Announcement,StressEvaluate,User,Attendance
from datetime import datetime,timedelta
from app.database import get_db
from flask_login import login_required,current_user
from app.database import SessionLocal
from flask import jsonify
from sqlalchemy.orm import joinedload
import json



coach_bp = Blueprint("coach", __name__, url_prefix="/coach")


@coach_bp.route("/", methods=["GET"])
def dashboard():
    # 教練主控台，只顯示大按鈕（公告管理、點名）
    return render_template("coach/dashboard.html")

coach_bp.route("/profile", methods=["GET"])
@login_required
def view_profile():
    return render_template('coach/profile.html', user=current_user)



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
        



@coach_bp.route('/sleep_record', methods=['GET'])
@login_required
def sleep_record():
    if current_user.role != 'coach':
        flash("只有教練可以查看此頁面", "danger")
        return redirect(url_for('main.index'))

    athlete_id = request.args.get('athlete_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    with get_db() as db:
        athletes = db.query(User).filter(User.role == 'athlete').all()

        query = db.query(SleepRecord).options(joinedload(SleepRecord.athlete)).order_by(SleepRecord.record_date.desc())

        if athlete_id:
            query = query.filter(SleepRecord.athlete_id == athlete_id)
        if start_date:
            query = query.filter(SleepRecord.record_date >= start_date)
        if end_date:
            query = query.filter(SleepRecord.record_date <= end_date)

        records = query.all()

        # 計算睡眠時長
        for r in records:
            start_dt = datetime.combine(r.record_date, r.sleep_start)
            end_dt = datetime.combine(r.record_date, r.sleep_end)
            if end_dt <= start_dt:  # 跨日睡眠
                end_dt += timedelta(days=1)
            r.sleep_duration = end_dt - start_dt

    return render_template(
        'coach/sleep_record.html',
        athletes=athletes,
        records=records,
        selected_athlete=athlete_id,
        start_date=start_date,
        end_date=end_date
    )
@coach_bp.route("/api/announcements", methods=["GET"])
def api_announcements():
    with get_db() as session:
        announcements = (
            session.query(Announcement)
            .order_by(Announcement.date.desc())
            .limit(3)  # 最多回傳 3 則
            .all()
        )

        result = [
            {
                "title": a.title,
                "content": a.content,
                "created_at": a.date.strftime("%Y-%m-%d")
            }
            for a in announcements
        ]

        return jsonify(result)

@coach_bp.route('/stress_query', methods=['GET', 'POST'])
@login_required
def stress_query():
    db = SessionLocal()
    athletes = db.query(User).filter(User.role == "athlete").all()
    result = None
    suggestion = ""
    score = None  # 總分也一起傳給模板

    if request.method == 'POST':
        athlete_id = request.form.get("athlete_id")

        result = (
            db.query(StressEvaluate)
            .filter(StressEvaluate.athlete_id == athlete_id)
            .order_by(StressEvaluate.timestamp.desc())
            .first()
        )

        if result:
            # 計算壓力總分
            score = sum([
                result.q1, result.q2, result.q3, result.q4, result.q5, result.q6,
                result.q7, result.q8, result.q9, result.q10, result.q11, result.q12,
                result.q13, result.q14, result.q15, result.q16, result.q17
            ])

            # 根據分數給建議
            if score <= 40:
                suggestion = "壓力狀況良好，請持續保持！"
            elif score <= 70:
                suggestion = "壓力略高，建議適度放鬆與休息。"
            else:
                suggestion = "壓力過高，請儘速尋求協助或諮詢專業人員。"

    db.close()
    return render_template(
        "coach/stress_record.html",
        athletes=athletes,
        result=result,
        score=score,
        suggestion=suggestion
    )
    
@coach_bp.route('/assign_training', methods=['GET', 'POST'])
def assign_training():
    db = SessionLocal()

    athlete_id = request.args.get('athlete_id')
    date = request.args.get('date')

    # 取所有選手清單
    athletes = db.query(User).all()  # 假設 User 是選手模型

    if request.method == 'POST':
        athlete_id = request.form.get('athlete_id') or athlete_id
        date = request.form.get('date') or date

    record = db.query(Training).filter_by(user_id=athlete_id, date=date).first()

    if not record:
        record = Training(user_id=athlete_id, date=date)

    if request.method == 'POST':
        record.coach_assigned_physical = request.form.get('coach_assigned_physical', '')

        technical_items = []
        categories = request.form.getlist('technical_category[]')
        topics = request.form.getlist('technical_topic[]')
        durations = request.form.getlist('technical_duration[]')
        focuses = request.form.getlist('technical_focus[]')

        for cat, top, dur, foc in zip(categories, topics, durations, focuses):
            if cat.strip() or top.strip():
                technical_items.append({
                    "category": cat.strip(),
                    "topic": top.strip(),
                    "duration_or_reps": dur.strip(),
                    "focus": foc.strip()
                })

        record.coach_assigned_technical = json.dumps(technical_items, ensure_ascii=False)

        db.add(record)
        db.commit()
        db.close()

        return redirect(url_for('coach.assign_training', athlete_id=athlete_id, date=date))

    db.close()
    # 一定要傳 athletes 給模板
    return render_template('coach/coach_assign_training.html', record=record, athletes=athletes)

