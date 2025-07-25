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
from app.routes.training import training_bp
from app.routes.evaluation import evaluation_bp
from app.routes.athlete import athlete_bp
from app.routes.chat import chat_bp
from app.routes.line_bot import line_bp
from app.models import User
from app.models.announcement import Announcement
from app.models.sleep_record import SleepRecord 
from app.routes.stress_evaluate import stress_bp
from app.models.stress_evaluate import StressEvaluate


from dotenv import load_dotenv




def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    Base.metadata.create_all(bind=engine)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 指定未登入者會被導向的登入頁面 endpoint

    app.register_blueprint(coach_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(line_bp)
    app.register_blueprint(training_bp,url_prefix='/training')
    app.register_blueprint(evaluation_bp, url_prefix='/evaluation')
    app.register_blueprint(athlete_bp)
    app.register_blueprint(stress_bp, url_prefix='/stress')
    
    
    
    
    @login_manager.user_loader
    def load_user(user_id):
        db = SessionLocal()
        user = db.query(User).get(int(user_id))
        db.close()
        return user 

    return app


