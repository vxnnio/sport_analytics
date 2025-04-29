from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.database import get_db
from app.database import SessionLocal
from flask import abort

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/create_coach', methods=['GET', 'POST'])
@login_required
def create_coach():
    

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

@admin_bp.route('/management', methods=['GET'])
@login_required
def user_management():

    keyword = request.args.get('keyword', '')
    role = request.args.get('role', '')

    # 使用 session 來查詢資料
    db = SessionLocal()
    query = db.query(User)

    if keyword:
        query = query.filter(User.username.contains(keyword))
    if role:
        query = query.filter_by(role=role)

    users = query.all()
    return render_template('admin/user_management.html', users=users)

@admin_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    db = SessionLocal()
    
    user = db.query(User).get(user_id)
    if not user:
        abort(404)

    if request.method == 'POST':
        new_username = request.form['username']
        new_role = request.form['role']
        new_password = request.form['password']

        # 檢查是否已存在同名使用者（排除自己）
        existing_user = db.query(User).filter(User.username == new_username, User.id != user_id).first()
        if existing_user:
            flash('使用者名稱已存在')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        user.username = new_username
        user.role = new_role
        if new_password:
            user.password = generate_password_hash(new_password)

        db.commit()
        flash('✅ 使用者資料已更新')
        return redirect(url_for('admin.user_management'))

    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    db = SessionLocal()  # 建立新的資料庫會話

    user = db.query(User).get(user_id)  # 查詢使用者
    if not user:
        abort(404)  # 如果找不到用戶，回傳 404 錯誤

    db.delete(user)  # 刪除使用者
    db.commit()  # 提交變更
    flash('🗑️ 使用者已刪除')  # 顯示提示訊息

    return redirect(url_for('admin.user_management'))  # 重定向到用戶管理頁面

@admin_bp.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('admin.user_management'))

    return render_template('admin/register.html')