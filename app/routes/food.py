import os
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.database import get_db

bp = Blueprint('food', __name__, url_prefix='/food')

UPLOAD_FOLDER = 'uploads/food'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET', 'POST'])
def upload_food():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('沒有檔案')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('沒有選擇檔案')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            # 確保資料夾存在
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(save_path)

            with get_db() as db:
                db.execute(
                    text(
                        "INSERT INTO food_photos (athlete_id, filename, upload_time) "
                        "VALUES (:athlete_id, :filename, :upload_time)"
                    ),
                    {"athlete_id": 1, "filename": filename, "upload_time": datetime.now()}
                )
                db.commit()

            flash('上傳成功')
            return redirect(url_for('food.view_food'))
    return render_template('athlete/upload_food.html')

@bp.route('/view')
def view_food():
    with get_db() as db:
        photos = db.execute(
            text("SELECT * FROM food_photos ORDER BY upload_time DESC")
        ).fetchall()
    return render_template('coach/view_food.html', photos=photos)

@bp.route('/comment/<int:photo_id>', methods=['POST'])
def comment_food(photo_id):
    comment = request.form.get('comment')
    with get_db() as db:
        db.execute(
            text(
                "UPDATE food_photos SET comment=:comment, comment_time=:comment_time WHERE id=:photo_id"
            ),
            {"comment": comment, "comment_time": datetime.now(), "photo_id": photo_id}
        )
        db.commit()
    flash('評論已送出')
    return redirect(url_for('food.view_food'))

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    full_path = os.path.abspath(UPLOAD_FOLDER)
    print(f"Serving file from: {full_path}, filename: {filename}")
    return send_from_directory(full_path, filename)



