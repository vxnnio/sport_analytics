# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_user, logout_user, login_required, current_user
# from app.models.user import User,Announcement
# from werkzeug.security import check_password_hash
# from app import db

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()

#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             if user.role == 'coach':
#                 return redirect(url_for('coach.dashboard'))
#             elif user.role == 'athlete':
#                 return redirect(url_for('auth.dashboard'))
#             else:
#                 return redirect(url_for('auth.admin_dashboard'))
#         flash('帳號或密碼錯誤')
#     return render_template('login.html')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('auth.login'))

# @auth_bp.route('/dashboard')
# @login_required
# def dashboard():
#     # 根據當前用戶的 id 查詢該用戶作為教練發布的公告
#     announcements = Announcement.query.all()
#     print(announcements)  # 在終端檢查是否有資料
    
#     # 傳遞 announcements 變數到模板中
#     return render_template('dashboard.html', announcements=announcements)



# from werkzeug.security import generate_password_hash  # 確保有匯入這行

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']  # athlete / coach

#         if User.query.filter_by(username=username).first():
#             flash('使用者名稱已存在')
#             return redirect(url_for('auth.register'))

#         new_user = User(
#             username=username,
#             password=generate_password_hash(password),
#             role=role
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash('註冊成功，請登入')
#         return redirect(url_for('auth.login'))

#     return render_template('register.html')


# @auth_bp.route('/admin/dashboard')
# @login_required
# def admin_dashboard():
#     if current_user.role != 'admin':
#         flash('您不是管理員')
#         return redirect(url_for('auth.dashboard'))
    
#     return render_template('admin_dashboard.html')


# @auth_bp.route('/admin/create_coach', methods=['GET', 'POST'])
# @login_required
# def create_coach():
#     # 🛡️ 限制只有 admin 可以進入
#     if current_user.role != 'admin':
#         flash('您沒有權限進行此操作')
#         return redirect(url_for('auth.dashboard'))  # 根據你自己有的 dashboard 調整

#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if User.query.filter_by(username=username).first():
#             flash('使用者名稱已存在')
#             return redirect(url_for('auth.create_coach'))

#         new_user = User(
#             username=username,
#             password=generate_password_hash(password),
#             role='coach'
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash('✅ 教練帳號已成功建立！')
#         return redirect(url_for('auth.admin_dashboard'))  # 或導回 admin 控制台

#     return render_template('create_coach.html')

# @auth_bp.route('/admin/create_athlete', methods=['GET', 'POST'])
# @login_required
# def create_athlete():
#     if current_user.role != 'admin':
#         flash('您沒有權限進行此操作')
#         return redirect(url_for('auth.dashboard'))

#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # 檢查使用者名稱是否已存在
#         if User.query.filter_by(username=username).first():
#             flash('⚠️ 此使用者名稱已存在，請使用其他名稱')
#             return redirect(url_for('auth.create_athlete'))

#         new_user = User(
#             username=username,
#             password=generate_password_hash(password),
#             role='athlete'
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash('✅ 成功新增選手帳號！')
#         return redirect(url_for('auth.user_management'))

#     return render_template('create_athlete.html')


# @auth_bp.route('/admin/management', methods=['GET'])
# @login_required
# def user_management():
#     if current_user.role != 'admin':
#         flash('您沒有權限進入此頁面')
#         return redirect(url_for('auth.dashboard'))

#     keyword = request.args.get('keyword', '')
#     role = request.args.get('role', '')

#     query = User.query

#     if keyword:
#         query = query.filter(User.username.contains(keyword))
#     if role:
#         query = query.filter_by(role=role)

#     users = query.all()

#     return render_template('user_management.html', users=users)


# from werkzeug.security import generate_password_hash

# @auth_bp.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
# @login_required
# def edit_user(user_id):
#     if current_user.role != 'admin':
#         flash('您沒有權限進行此操作')
#         return redirect(url_for('auth.dashboard'))

#     user = User.query.get_or_404(user_id)

#     if request.method == 'POST':
#         new_username = request.form['username']
#         new_role = request.form['role']
#         new_password = request.form['password']

#         # 檢查是否使用者名稱已存在（但不是這個人）
#         if user.username != new_username and User.query.filter_by(username=new_username).first():
#             flash('使用者名稱已存在')
#             return redirect(url_for('auth.edit_user', user_id=user_id))

#         user.username = new_username
#         user.role = new_role

#         if new_password:
#             user.password = generate_password_hash(new_password)

#         db.session.commit()
#         flash('✅ 使用者資料已更新')
#         return redirect(url_for('auth.user_management'))

#     return render_template('edit_user.html', user=user)


# @auth_bp.route('/admin/delete/<int:user_id>', methods=['POST'])
# @login_required
# def delete_user(user_id):
#     if current_user.role != 'admin':
#         flash('您沒有權限進行此操作')
#         return redirect(url_for('auth.dashboard'))

#     user = User.query.get_or_404(user_id)

#     db.session.delete(user)
#     db.session.commit()

#     flash('🗑️ 使用者已刪除')
#     return redirect(url_for('auth.user_management'))



