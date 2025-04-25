from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Announcement
from app.database import get_db
from sqlalchemy.orm import Session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 使用 get_db() 方法來獲取資料庫會話
        with get_db() as db:
            user = db.query(User).filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                if user.role == 'coach':
                    return redirect(url_for('coach.dashboard'))
                elif user.role == 'athlete':
                    return redirect(url_for('auth.dashboard'))
                else:
                    return redirect(url_for('admin.admin_dashboard'))
            
            flash('帳號或密碼錯誤')
    return render_template('shared/login.html')
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    announcements = Announcement.query.all()
    return render_template('dashboard.html', announcements=announcements)

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
