from flask import Flask
from app.config import Config
from app.database import SessionLocal
from app.database import engine, Base
from flask_login import LoginManager
from app.routes.coach import coach_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.main import main_bp
from app.routes.profile import profile_bp
from app.routes.evaluation import evaluation_bp
from app.routes.athlete import athlete_bp
from app.routes.chat import chat_bp
from app.routes.food import bp as food_bp
import os,json
from app.routes.voice import voice_bp
from app.routes.line_bot import line_bp
from app.routes.food import bp as food_bp
from app.models import User
from app.models.announcement import Announcement
from app.models.sleep_record import SleepRecord 
from app.routes.stress_evaluate import stress_bp
from app.models.stress_evaluate import StressEvaluate
from app.models.food_photo import FoodPhoto
target_metadata = Base.metadata

from dotenv import load_dotenv

# ⬇️ 匯入你 line_bot 那邊的 create_rich_menu
from app.routes.line_bot import create_rich_menu  

UPLOAD_FOLDER = 'uploads/food'

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    Base.metadata.create_all(bind=engine)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.register_blueprint(coach_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(line_bp)
    app.register_blueprint(evaluation_bp, url_prefix='/evaluation')
    app.register_blueprint(athlete_bp)
    app.register_blueprint(food_bp)  # 新增這一行
    app.register_blueprint(voice_bp)
    app.register_blueprint(chat_bp, url_prefix='/chatbot')
    app.register_blueprint(stress_bp)

    @login_manager.user_loader
    def load_user(user_id):
        db = SessionLocal()
        user = db.query(User).get(int(user_id))
        db.close()
        return user 

    # ⚡️這裡呼叫 Rich Menu 建立
    try:
        create_rich_menu()
    except Exception as e:
        print(f"[RichMenu Error] {e}")
    # 註冊 from_json 過濾器
    @app.template_filter('from_json')
    def from_json_filter(s):
        if s:
            return json.loads(s)
        return []
    return app


