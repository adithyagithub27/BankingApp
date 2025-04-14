from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, current_user
from app.auth import auth_bp
from app.admin import admin_bp
from app.dashboard import dashboard_bp
from app.fixeddeposit import fixeddeposit_bp
from app.profile import profile_bp
from app.transfer import transfer_bp
from app import db
from app.models import User  # Make sure your User model is imported
from app.api.users_api import users_api_bp


from flasgger import Swagger
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object('config.Config')  # load config
app.config['SESSION_PERMANENT'] = False  # Session will expire on browser close
# Initialize the database
db.init_app(app)

# Create the database tables (for development only, use migrations in production)
with app.app_context():
    db.create_all()

# Initialize JWT Manager for token-based authentication
jwt = JWTManager(app)

# Initialize Swagger
swagger = Swagger(app)

# Initialize Flask-Login and register user loader
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure current_user is available in all templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Register blueprints for frontend and API endpoints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(fixeddeposit_bp, url_prefix='/fixeddeposit')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(transfer_bp, url_prefix='/transfer')
app.register_blueprint(users_api_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
