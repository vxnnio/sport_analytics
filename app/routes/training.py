# # app/routes/api_training.py
# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from app.database import get_db
# from app.models.training import Training

# api_training_bp = Blueprint("api_training", __name__, url_prefix="/api/trainings")


# @api_training_bp.route("", methods=["GET", "POST"])
# @login_required
# def trainings():
#     with get_db() as db:
#         if request.method == "GET":
#             recs = (
#                 db.query(Training)
#                 .filter_by(user_id=current_user.id)
#                 .order_by(Training.date.desc())
#                 .all()
#             )
#             return jsonify([r.to_dict() for r in recs]), 200

#         data = request.get_json()
#         new = Training(user_id=current_user.id, **data)
#         db.add(new)
#         db.commit()
#         db.refresh(new)
#         return jsonify(new.to_dict()), 201


# @api_training_bp.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
# @login_required
# def training_detail(id):
#     with get_db() as db:
#         rec = db.query(Training).get(id)
#         if not rec or rec.user_id != current_user.id:
#             return jsonify({"error": "Not found"}), 404

#         if request.method == "GET":
#             return jsonify(rec.to_dict()), 200

#         if request.method == "PUT":
#             for k, v in request.get_json().items():
#                 setattr(rec, k, v)
#             db.commit()
#             return jsonify(rec.to_dict()), 200

#         # DELETE
#         db.delete(rec)
#         db.commit()
#         return "", 204
