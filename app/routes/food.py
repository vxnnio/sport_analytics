import os
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.database import get_db
from flask_login import current_user, login_required


bp = Blueprint('food', __name__, url_prefix='/food')

UPLOAD_FOLDER = 'uploads/food'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_food():
    if request.method == 'POST':
        file = request.files.get('photo')
        if file:
            filename = file.filename
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            with get_db() as db:
                db.execute(
    text(
        "INSERT INTO food_photos (athlete_id, athlete_username, filename, upload_time) "
        "VALUES (:athlete_id, :athlete_username, :filename, :upload_time)"
    ),
    {
        "athlete_id": current_user.id,
        "athlete_username": current_user.username,
        "filename": filename,
        "upload_time": datetime.now()
    }
)


                db.commit()
            flash('上傳成功')
            return redirect(url_for('food.upload_food'))

    with get_db() as db:
        photos = db.execute(
            text("SELECT * FROM food_photos WHERE athlete_id=:uid ORDER BY upload_time DESC"),
            {"uid": current_user.id}
        ).fetchall()

    return render_template('athlete/upload_food.html', photos=photos)

@bp.route('/view')
def view_food():
    with get_db() as db:
        photos = db.execute(
            text("SELECT * FROM food_photos ORDER BY upload_time DESC")
        ).fetchall()
    return render_template('coach/view_food.html', photos=photos)

@bp.route('/comment/<int:photo_id>', methods=['POST'])
def comment_food(photo_id):
    comment_text = request.form.get('comment')
    if not comment_text:
        flash("評論不能為空", "warning")
        return redirect(url_for('food.view_food'))

    with get_db() as db:
        # 確認這張照片存在
        photo = db.execute(
            text("SELECT * FROM food_photos WHERE id=:photo_id"),
            {"photo_id": photo_id}
        ).fetchone()

        if not photo:
            flash("找不到該照片", "danger")
            return redirect(url_for('food.view_food'))

        # 更新評論和時間
        db.execute(
            text(
                "UPDATE food_photos "
                "SET comment=:comment, comment_time=:comment_time "
                "WHERE id=:photo_id"
            ),
            {"comment": comment_text, "comment_time": datetime.now(), "photo_id": photo_id}
        )
        db.commit()

    flash("評論已送出", "success")
    return redirect(url_for('food.view_food'))

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    full_path = os.path.abspath(UPLOAD_FOLDER)
    print(f"Serving file from: {full_path}, filename: {filename}")
    return send_from_directory(full_path, filename)



