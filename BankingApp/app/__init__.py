import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    # Point template_folder to the "templates" folder at the project root
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"))
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints (example)
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.transfer import transfer_bp
    from app.profile import profile_bp
    from app.fixeddeposit import fixeddeposit_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(fixeddeposit_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()
    
    return app
