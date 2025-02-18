# app/models.py
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False, default="customer")  # 'customer' or 'admin'
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships can be added here for accounts, transactions, etc.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_account = db.Column(db.String(64))
    to_account = db.Column(db.String(64))
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))

class FixedDeposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)  # in years (or fraction)
    interest_rate = db.Column(db.Float, nullable=False)
    maturity_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
