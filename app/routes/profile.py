from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os
from flask import current_app
from werkzeug.utils import secure_filename
from app.database import SessionLocal
from app.models.user import User  # 依你的使用者模型路徑調整

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/')
@login_required
def view_profile():
    return render_template('shared/profile.html', user=current_user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # 接收表單資料
        full_name = request.form.get('full_name')
        birth_date = request.form.get('birth_date')  # yyyy-mm-dd 格式
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        region = request.form.get('region')
        bio = request.form.get('bio')
        file = request.files.get('profile_pic')

        db = SessionLocal()
        user = db.query(User).filter(User.id == current_user.id).first()

        # 更新文字欄位
        if full_name:
            user.full_name = full_name
        if birth_date:
            user.birth_date = birth_date
        if gender:
            user.gender = gender
        if height:
            user.height = int(height) if height else None
        if weight:
            user.weight = int(weight) if weight else None
        if region:
            user.region = region
        if bio:
            user.bio = bio

        # 上傳圖片
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            user.profile_pic = f'uploads/profile_pics/{filename}'

        db.commit()
        db.close()

        flash('更新成功')
        return redirect(url_for('profile.view_profile'))

    return render_template('shared/edit_profile.html', user=current_user)
