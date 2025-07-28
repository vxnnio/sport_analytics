from .auth import auth_bp
# from .training import training_bp
from .main import main_bp
from .coach import coach_bp
from .admin import admin_bp
from .profile import profile_bp
from .stress_evaluate import stress_bp
# from .evaluation import evaluation_bp

__all__ = ["coach_bp",
           "main_bp",
           "auth_bp",
           "admin_bp",
           "profile_bp",
           "stress_bp"]
