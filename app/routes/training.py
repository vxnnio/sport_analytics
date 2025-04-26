from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.database import get_db
from app.models.training import Training
from datetime import datetime
from app.models.evaluation import Evaluation # ✅ 新增這行
from app.models.announcement import Announcement
from app.database import get_db  # 引入 get_db

training_bp = Blueprint('training', __name__)

@training_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_training():
    if request.method == 'POST':
        with get_db() as db:
            try:
                record = Training(
                    user_id=current_user.id,
                    date=datetime.strptime(request.form['date'], "%Y-%m-%d").date(),
                    jump_type=request.form.get('jump_type'),
                    jump_count=int(request.form.get('jump_count') or 0),
                    run_distance=float(request.form.get('run_distance') or 0),
                    run_time=request.form.get('run_time'),
                    weight_part=request.form.get('weight_part'),
                    weight_sets=int(request.form.get('weight_sets') or 0),
                    agility_type=request.form.get('agility_type'),
                    agility_note=request.form.get('agility_note'),
                    special_focus=request.form.get('special_focus')
                )
                db.add(record)
                db.commit()
                flash("✅ 訓練紀錄已成功上傳")
                return redirect(url_for('training.training_history'))
            except Exception as e:
                db.rollback()
                flash(f"❌ 出錯了: {str(e)}")

    return render_template('athlete/upload.html')

@training_bp.route('/history')
@login_required
def training_history():
    with get_db() as db:  # 使用 get_db() 管理資料庫會話
        training_records = db.query(Training).filter_by(user_id=current_user.id).order_by(Training.date.desc()).all()
        evaluation_records = db.query(Evaluation).filter_by(user_id=current_user.id).order_by(Evaluation.eval_date.desc()).all()
    return render_template('athlete/all_records.html', trainings=training_records, evaluations=evaluation_records)


# ✅ 編輯訓練紀錄
@training_bp.route('/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    with get_db() as db:  # 使用 get_db() 管理資料庫會話
        record = db.query(Training).get_or_404(record_id)
        if record.user_id != current_user.id:
            return "無權限存取", 403

        if request.method == 'POST':
            record.date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
            record.time = request.form['time']
            record.heart_rate = float(request.form['heart_rate'])
            record.distance = float(request.form['distance'])
            record.menu = request.form['menu']
            db.commit()  # 提交變更
            flash("✅ 訓練紀錄已更新")
            return redirect(url_for('training.training_history'))

    return render_template('edit_record.html', record=record)

# ✅ 刪除訓練紀錄
@training_bp.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    with get_db() as db:  # 使用 get_db() 管理資料庫會話
        record = db.query(Training).get_or_404(record_id)
        if record.user_id != current_user.id:
            return "無權限刪除", 403

        db.delete(record)  # 刪除紀錄
        db.commit()  # 提交變更
        flash("🗑️ 已刪除一筆紀錄")
    return redirect(url_for('training.training_history'))


@training_bp.route('/api/announcements', methods=['GET'])
def get_announcements():
    with get_db() as db:  # 使用 get_db() 管理資料庫會話
        announcements = db.query(Announcement).all()
        data = [
            {
                'id': a.id,
                'title': a.title,
                'content': a.content
            }
            for a in announcements
        ]
    return jsonify(data), 200



