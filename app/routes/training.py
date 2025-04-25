from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.training import Training
from app.database import SessionLocal
from flask import abort

training_bp = Blueprint('training', __name__)

@training_bp.route('/dashboard')
@login_required
def training_dashboard():
    return render_template('training/dashboard.html')

@training_bp.route('/create_training', methods=['GET', 'POST'])
@login_required
def create_training():
    if request.method == 'POST':
        # 你可以根據需要調整
        data = request.form
        new_training = Training(
            user_id=current_user.id,
            title=data['title'],
            date=data['date'],
            details=data['details'],
        )
        db = SessionLocal()  # 創建資料庫 session
        db.add(new_training)
        db.commit()
        flash('✅ 訓練已成功創建！')
        return redirect(url_for('training.training_dashboard'))
    return render_template('training/create_training.html')

@training_bp.route('/edit/<int:training_id>', methods=['GET', 'POST'])
@login_required
def edit_training(training_id):
    db = SessionLocal()
    training = db.query(Training).get(training_id)
    
    if not training or training.user_id != current_user.id:
        abort(404)

    if request.method == 'POST':
        training.title = request.form['title']
        training.date = request.form['date']
        training.details = request.form['details']
        
        db.commit()
        flash('✅ 訓練資料已更新')
        return redirect(url_for('training.training_dashboard'))

    return render_template('training/edit_training.html', training=training)

@training_bp.route('/delete/<int:training_id>', methods=['POST'])
@login_required
def delete_training(training_id):
    db = SessionLocal()
    training = db.query(Training).get(training_id)
    
    if not training or training.user_id != current_user.id:
        abort(404)

    db.delete(training)
    db.commit()
    flash('🗑️ 訓練已刪除')
    return redirect(url_for('training.training_dashboard'))
