from flask import Flask
from app.config import Config
from app.database import SessionLocal
from app.database import engine, Base
from flask_login import LoginManager
from app.routes.coach import coach_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.main import main_bp
from app.models import User
from dotenv import load_dotenv
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Base.metadata.create_all(bind=engine)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    app.register_blueprint(coach_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        db = SessionLocal()
        user = db.query(User).get(int(user_id))
        db.close()
        return user 

    return app


