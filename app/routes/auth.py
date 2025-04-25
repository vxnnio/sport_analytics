from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Announcement
from app.database import get_db
from sqlalchemy.orm import Session
from flask_login import login_required
from app.database import SessionLocal


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as db:
            # 查詢用戶
            user = db.query(User).filter_by(username=username).first()

            if user:  # 如果找到使用者
                # 檢查密碼
                if check_password_hash(user.password, password):
                    login_user(user)

                    # 根據角色重定向到不同的頁面
                    if user.role == 'coach':
                        return redirect(url_for('coach.dashboard'))
                    elif user.role == 'athlete':
                        return redirect(url_for('auth.dashboard'))
                    elif user.role == 'admin':
                        return redirect(url_for('admin.admin_dashboard'))
                    else:
                        flash('未知的使用者角色')
                        return redirect(url_for('auth.login'))
                else:
                    flash('密碼錯誤')
            else:
                flash('帳號不存在')

            return render_template('shared/login.html')  # 密碼錯誤或帳號不存在，都顯示錯誤並重導

    return render_template('shared/login.html')  # 初次加載登入頁面

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    session = SessionLocal()
    try:
        announcements = session.query(Announcement).all()
        return render_template('athlete/dashboard.html', announcements=announcements)
    finally:
        session.close()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        with get_db() as db:  # 用 contextmanager 開啟 session
            existing_user = db.query(User).filter_by(username=username).first()
            if existing_user:
                flash('使用者名稱已存在')
                return redirect(url_for('auth.register'))  # 修正這裡的 endpoint 名稱

            new_user = User(
                username=username,
                password=generate_password_hash(password),
                role=role
            )
            db.add(new_user)
            db.commit()

            flash('註冊成功，請登入')
            return redirect(url_for('auth.login'))

    return render_template('shared/register.html')
