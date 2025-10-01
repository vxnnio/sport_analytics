from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import SleepRecord,Announcement,StressEvaluate,User,Attendance
from app.models.task import Task
from datetime import datetime,timedelta
from app.database import get_db
from flask_login import login_required,current_user
from app.database import SessionLocal
from flask import jsonify
from sqlalchemy.orm import joinedload
from sqlalchemy import func, Integer
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
    


@coach_bp.route("/tasks", methods=["GET"])
def view_tasks():
    with get_db() as db:
        tasks = db.query(Task).options(joinedload(Task.athlete)).all()
        athletes = db.query(User).filter_by(role="athlete").all()  # ✅ 查出所有學生
    return render_template("coach/training.html", tasks=tasks, athletes=athletes)


# 派發任務
@coach_bp.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    athlete_id = data.get("athlete_id")  # 可指定學生
    with get_db() as db:
        new_task = Task(
            category=data["category"],
            item=data["item"],
            description=data["description"],
            athlete_id=athlete_id
        )
        db.add(new_task)
        db.commit()
        return jsonify({"status": "success", "task_id": new_task.id})
    
# 修改任務
@coach_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    with get_db() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"status": "error", "message": "任務不存在"}), 404
        
        # 更新欄位
        task.category = data.get("category", task.category)
        task.item = data.get("item", task.item)
        task.description = data.get("description", task.description)
        task.athlete_id = data.get("athlete_id", task.athlete_id)

        db.commit()
        return jsonify({"status": "success", "task_id": task.id})

# 刪除任務
@coach_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_db() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"status": "error", "message": "任務不存在"}), 404
        
        db.delete(task)
        db.commit()
        return jsonify({"status": "success", "message": f"任務 {task_id} 已刪除"})

@coach_bp.route("/analysis")
def analysis():
    db = SessionLocal()
    students = db.query(User).filter(User.role=="athlete").all()

    stats = []
    for s in students:
        tasks = db.query(Task).filter(Task.athlete_id==s.id).all()
        strength_total = sum(1 for t in tasks if t.category=="體能")
        strength_completed = sum(1 for t in tasks if t.category=="體能" and t.completed)
        skill_total = sum(1 for t in tasks if t.category=="技巧")
        skill_completed = sum(1 for t in tasks if t.category=="技巧" and t.completed)
        total = len(tasks)
        total_completed = sum(1 for t in tasks if t.completed)

        stats.append({
            "full_name": s.full_name,
            "username": s.username,
            "strength_total": strength_total,
            "strength_completed": strength_completed,
            "skill_total": skill_total,
            "skill_completed": skill_completed,
            "total": total,
            "total_completed": total_completed
        })

    return render_template("coach/analysis.html", stats=stats)