from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.database import get_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('您不是管理員')
        return redirect(url_for('auth.dashboard'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/create_coach', methods=['GET', 'POST'])
@login_required
def create_coach():
    if current_user.role != 'admin':
        flash('您沒有權限進行此操作')
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('使用者名稱已存在')
            return redirect(url_for('admin.create_coach'))

        new_user = User(username=username, password=generate_password_hash(password), role='coach')
        db.session.add(new_user)
        db.session.commit()
        flash('✅ 教練帳號已成功建立！')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('create_coach.html')

@admin_bp.route('/admin/create_athlete', methods=['GET', 'POST'])
@login_required
def create_athlete():
    if current_user.role != 'admin':
        flash('您沒有權限進行此操作')
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('⚠️ 此使用者名稱已存在，請使用其他名稱')
            return redirect(url_for('admin.create_athlete'))

        new_user = User(username=username, password=generate_password_hash(password), role='athlete')
        db.session.add(new_user)
        db.session.commit()
        flash('✅ 成功新增選手帳號！')
        return redirect(url_for('admin.user_management'))

    return render_template('create_athlete.html')

@admin_bp.route('/admin/management', methods=['GET'])
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('您沒有權限進入此頁面')
        return redirect(url_for('auth.dashboard'))

    keyword = request.args.get('keyword', '')
    role = request.args.get('role', '')

    query = User.query
    if keyword:
        query = query.filter(User.username.contains(keyword))
    if role:
        query = query.filter_by(role=role)

    users = query.all()
    return render_template('user_management.html', users=users)

@admin_bp.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('您沒有權限進行此操作')
        return redirect(url_for('auth.dashboard'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_username = request.form['username']
        new_role = request.form['role']
        new_password = request.form['password']

        if user.username != new_username and User.query.filter_by(username=new_username).first():
            flash('使用者名稱已存在')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        user.username = new_username
        user.role = new_role
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('✅ 使用者資料已更新')
        return redirect(url_for('admin.user_management'))

    return render_template('edit_user.html', user=user)

@admin_bp.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('您沒有權限進行此操作')
        return redirect(url_for('auth.dashboard'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('🗑️ 使用者已刪除')
    return redirect(url_for('admin.user_management'))
