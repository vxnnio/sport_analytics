from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.database import get_db  # 使用 get_db() 來獲取資料庫會話
from app.models.evaluation import Evaluation
from datetime import date

# ✅ 藍圖註冊
evaluation_bp = Blueprint('evaluation', __name__)

# ✅ 每日訓練狀況評估表單（新增）
@evaluation_bp.route('/form', methods=['GET', 'POST'])
@login_required
def evaluate_today():
    if request.method == 'POST':
        # 使用 get_db() 管理資料庫會話
        with get_db() as db:
            record = Evaluation(
                user_id=current_user.id,
                eval_date=date.today(),
                training_status=request.form['training_status'],
                fitness=request.form['fitness'],
                sleep=request.form['sleep'],
                appetite=request.form['appetite'],
                note=request.form.get('note')
            )
            db.add(record)  # 將資料加入資料庫
            db.commit()  # 提交變更
        flash("✅ 今日訓練狀況已送出")
        return redirect(url_for('auth.dashboard'))
    return render_template('athlete/evaluation_form.html')

# ✅ 編輯評估紀錄
@evaluation_bp.route('/edit/<int:eval_id>', methods=['GET', 'POST'])
@login_required
def edit_evaluation(eval_id):
    db = get_db()  # 獲取資料庫會話
    record = Evaluation.query.get_or_404(eval_id)
    if record.user_id != current_user.id:
        return "無權限存取", 403

    if request.method == 'POST':
        record.training_status = request.form['training_status']
        record.fitness = request.form['fitness']
        record.sleep = request.form['sleep']
        record.appetite = request.form['appetite']
        record.note = request.form.get('note')
        db.session.commit()
        flash("✅ 評估紀錄已更新")
        return redirect(url_for('training.training_history'))  # ✅ 導向全部紀錄
    return render_template('edit_evaluation.html', record=record)

# ✅ 刪除評估紀錄
@evaluation_bp.route('/delete/<int:eval_id>', methods=['POST'])
@login_required
def delete_evaluation(eval_id):
    db = get_db()  # 獲取資料庫會話
    record = Evaluation.query.get_or_404(eval_id)
    if record.user_id != current_user.id:
        return "無權限刪除", 403

    db.session.delete(record)
    db.session.commit()
    flash("🗑️ 已刪除一筆評估紀錄")
    return redirect(url_for('training.training_history'))  # ✅ 導向全部紀錄
