from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.training import Training
from app.database import SessionLocal
from flask import abort
from sqlalchemy.exc import SQLAlchemyError

training_bp = Blueprint('training', __name__)

@training_bp.route('/dashboard')
@login_required
def training_dashboard():
    db = SessionLocal()
    try:
        trainings = db.query(Training).filter_by(user_id=current_user.id).order_by(Training.date.desc()).all()
        return render_template('training/dashboard.html', trainings=trainings)
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error: {str(e)}")
        abort(500)
    finally:
        db.close()

@training_bp.route('/create_training', methods=['GET', 'POST'])
@login_required
def create_training():
    if request.method == 'POST':
        db = SessionLocal()
        try:
            data = request.form
            new_training = Training(
                user_id=current_user.id,
                title=data['title'],
                date=data['date'],
                details=data['details'],
            )
            db.add(new_training)
            db.commit()
            flash('✅ 训练已成功创建！', 'success')
            return redirect(url_for('training.training_dashboard'))
        except SQLAlchemyError as e:
            db.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            flash('❌ 创建训练时出错', 'error')
        finally:
            db.close()
    return render_template('training/create_training.html')

@training_bp.route('/edit/<int:training_id>', methods=['GET', 'POST'])
@login_required
def edit_training(training_id):
    db = SessionLocal()
    try:
        training = db.query(Training).get(training_id)
        
        if not training or training.user_id != current_user.id:
            abort(404)

        if request.method == 'POST':
            try:
                training.title = request.form['title']
                training.date = request.form['date']
                training.details = request.form['details']
                db.commit()
                flash('✅ 训练资料已更新', 'success')
                return redirect(url_for('training.training_dashboard'))
            except SQLAlchemyError as e:
                db.rollback()
                current_app.logger.error(f"Database error: {str(e)}")
                flash('❌ 更新训练时出错', 'error')

        return render_template('training/edit_training.html', training=training)
    finally:
        db.close()

@training_bp.route('/delete/<int:training_id>', methods=['POST'])
@login_required
def delete_training(training_id):
    db = SessionLocal()
    try:
        training = db.query(Training).get(training_id)
        
        if not training or training.user_id != current_user.id:
            abort(404)

        db.delete(training)
        db.commit()
        flash('🗑️ 训练已删除', 'success')
        return redirect(url_for('training.training_dashboard'))
    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        flash('❌ 删除训练时出错', 'error')
        return redirect(url_for('training.training_dashboard'))
    finally:
        db.close()