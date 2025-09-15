import os
from uuid import uuid4
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.database import get_db
from flask_login import current_user, login_required

# Blueprint 註冊
bp = Blueprint('food', __name__, url_prefix='/food')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_food_upload_folder() -> str:
    # 存放在 <project>/static/uploads/food
    return os.path.join(current_app.root_path, 'static', 'uploads', 'food')

def check_athlete_exists(db, athlete_id: int) -> bool:
    """檢查用戶是否存在且是運動員"""
    result = db.execute(
        text("SELECT id FROM user WHERE id = :athlete_id AND role = 'athlete'"),
        {"athlete_id": athlete_id}
    ).fetchone()
    return result is not None

# ----------------------------
# 上傳照片
# ----------------------------
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_food():
    if request.method == 'POST':
        athlete_id = request.form.get('athlete_id', type=int) or 1  # 可改為 current_user.id

        if 'photo' not in request.files:
            flash('沒有選擇檔案', 'error')
            return redirect(request.url)

        file = request.files['photo']
        if not file or file.filename == '':
            flash('沒有選擇檔案', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('檔案類型只允許：png, jpg, jpeg', 'error')
            return redirect(request.url)

        # 生成唯一檔名
        base_name = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique = uuid4().hex[:6]
        filename = f"{timestamp}_{unique}_{base_name}"

        upload_folder = get_food_upload_folder()
        os.makedirs(upload_folder, exist_ok=True)
        save_path = os.path.join(upload_folder, filename)

        try:
            file.save(save_path)

            with get_db() as db:
                if not check_athlete_exists(db, athlete_id):
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    flash(f'運動員ID {athlete_id} 不存在或沒有權限', 'error')
                    return redirect(request.url)

                db.execute(
                    text(
                        "INSERT INTO food_photos (athlete_id, filename, upload_time) "
                        "VALUES (:athlete_id, :filename, :upload_time)"
                    ),
                    {
                        "athlete_id": athlete_id,
                        "filename": filename,
                        "upload_time": datetime.now()
                    }
                )
                db.commit()

            flash('上傳成功', 'success')
            return redirect(url_for('food.view_food'))

        except Exception as e:
            current_app.logger.exception(f"上傳失敗: {str(e)}")
            if os.path.exists(save_path):
                os.remove(save_path)
            flash('上傳失敗，請稍後再試', 'error')
            return redirect(request.url)

    return render_template('athlete/upload_food.html')

# ----------------------------
# 查看照片
# ----------------------------
@bp.route('/view')
@login_required
def view_food():
    with get_db() as db:
        photos = db.execute(
            text("""
                SELECT fp.*, u.username, u.full_name 
                FROM food_photos fp 
                LEFT JOIN user u ON fp.athlete_id = u.id 
                ORDER BY fp.upload_time DESC
            """)
        ).fetchall()
    return render_template('coach/view_food.html', photos=photos)

# ----------------------------
# 評論照片
# ----------------------------
@bp.route('/comment/<int:photo_id>', methods=['POST'])
@login_required
def comment_food(photo_id: int):
    comment = request.form.get('comment', '').strip()
    if not comment:
        flash('請輸入評論內容', 'error')
        return redirect(url_for('food.view_food'))

    with get_db() as db:
        photo = db.execute(
            text("SELECT * FROM food_photos WHERE id=:photo_id"),
            {"photo_id": photo_id}
        ).fetchone()

        if not photo:
            flash("找不到該照片", "error")
            return redirect(url_for('food.view_food'))

        db.execute(
            text(
                "UPDATE food_photos "
                "SET comment=:comment, comment_time=:comment_time "
                "WHERE id=:photo_id"
            ),
            {"comment": comment, "comment_time": datetime.now(), "photo_id": photo_id}
        )
        db.commit()

    flash('評論已送出', 'success')
    return redirect(url_for('food.view_food'))

# ----------------------------
# 刪除照片
# ----------------------------
@bp.route('/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_food(photo_id: int):
    with get_db() as db:
        photo = db.execute(
            text("SELECT filename FROM food_photos WHERE id = :photo_id"),
            {"photo_id": photo_id}
        ).mappings().fetchone()

        if not photo:
            flash('照片不存在', 'error')
            return redirect(url_for('food.view_food'))

        db.execute(
            text("DELETE FROM food_photos WHERE id = :photo_id"),
            {"photo_id": photo_id}
        )
        db.commit()

    # 刪除實體檔案
    file_path = os.path.join(get_food_upload_folder(), photo['filename'])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            current_app.logger.warning(f"刪除檔案失敗（DB 已刪除）：{file_path}，原因：{e}")

    flash('照片已刪除', 'success')
    return redirect(url_for('food.view_food'))
