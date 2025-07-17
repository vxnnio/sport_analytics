from flask import Blueprint, render_template, request, redirect, url_for

stress_bp = Blueprint('stress_evaluate', __name__)

# 顯示表單
@stress_bp.route("/evaluate", methods=["GET"])
def show_form():
    return render_template("athlete/stress_evaluate.html")

# 接收表單資料
@stress_bp.route("/evaluate", methods=["POST"])
def submit_form():
    data = {f"q{i}": request.form.get(f"q{i}") for i in range(1, 18)}
    print("表單接收到的資料：", data)

    return redirect(url_for("auth.dashboard"))

