import os, secrets
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from app.models.food_photo import FoodPhoto
from app.models.user import User
from app.database import get_db   
from flask import jsonify

bp = Blueprint("food", __name__, url_prefix="/food")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_food_upload_folder():
    return os.path.join(current_app.root_path, "static", "uploads", "food")

@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_food():
    if request.method == "POST":
        file = request.files.get("photo")
        if not file or file.filename == "":
            flash("請選擇照片", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("檔案類型只允許 png, jpg, jpeg", "danger")
            return redirect(request.url)

        # 建立安全檔名
        random_hex = secrets.token_hex(8)
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random_hex}_{filename}"

        upload_folder = get_food_upload_folder()
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        # 存到 DB
        new_photo = FoodPhoto(
            athlete_id=current_user.id,
            athlete_username=current_user.username,
            filename=filename,
            upload_time=datetime.now()
        )
        with get_db() as session:
            session.add(new_photo)
            session.commit()

        flash("照片上傳成功！", "success")
        return render_template("athlete/upload_food.html")

    return render_template("athlete/upload_food.html")


# ----------------------------
# 瀏覽所有食物照片
# ----------------------------
@bp.route("/view")
@login_required
def view_food():
    with get_db() as session:
        photos = (
            session.query(FoodPhoto)
            .options(joinedload(FoodPhoto.athlete))  # 如果 FoodPhoto 有 relationship
            .order_by(FoodPhoto.upload_time.desc())
            .all()
        )
    return render_template("coach/view_food.html", photos=photos)

# 教練評論
@bp.route("/comment/<int:photo_id>", methods=["POST"])
@login_required
def comment_food(photo_id):
    comment = request.form.get("comment", "").strip()
    if not comment:
        flash("請輸入評論內容", "error")
        return redirect(url_for("food.view_food"))

    with get_db() as session:
        photo = session.query(FoodPhoto).get(photo_id)
        if not photo:
            flash("找不到該照片", "error")
            return redirect(url_for("food.view_food"))

        photo.comment = comment
        photo.comment_time = datetime.now()
        session.commit()

    flash("評論已送出", "success")
    return redirect(url_for("food.view_food"))


# 刪除照片
@bp.route("/delete/<int:photo_id>", methods=["POST"])
@login_required
def delete_food(photo_id):
    with get_db() as session:
        photo = session.query(FoodPhoto).get(photo_id)
        if not photo:
            flash("照片不存在", "error")
            return redirect(url_for("food.view_food"))

        # 先刪掉檔案
        file_path = os.path.join(get_food_upload_folder(), photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # 刪掉 DB 紀錄
        session.delete(photo)
        session.commit()

    flash("照片已刪除", "success")
    return redirect(url_for("food.view_food"))

# ----------------------------
# 只讀飲食紀錄（評論不可編輯、不可刪除）
# ----------------------------
@bp.route("/records")
@login_required
def food_records():
    with get_db() as session:
        # 取得所有食物照片，最新上傳在前
        photos = (
            session.query(FoodPhoto)
            .order_by(FoodPhoto.upload_time.desc())
            .all()
        )
    # 渲染只讀模板
    return render_template("athlete/view_food_records.html", photos=photos)
