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
        bio = request.form.get('bio')
        file = request.files.get('profile_pic')

        db = SessionLocal()
        user = db.query(User).filter(User.id == current_user.id).first()

        if bio:
            user.bio = bio

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # 使用 Flask 實際根目錄計算上傳路徑
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # 儲存在資料庫中的是相對於 static 的路徑，供 url_for 使用
            user.profile_pic = f'uploads/profile_pics/{filename}'

        db.commit()
        db.close()
        flash('更新成功')
        return redirect(url_for('profile.view_profile'))

    return render_template('shared/edit_profile.html', user=current_user)
