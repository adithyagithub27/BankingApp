# app/dashboard.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Account, Transaction

dashboard_bp = Blueprint("dashboard", __name__)

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Account, Transaction

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Retrieve accounts for the current user
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    # Create a list of account numbers from the user's accounts
    account_numbers = [acc.account_number for acc in accounts]
    # Retrieve transactions where any of the user's account numbers appear
    transactions = Transaction.query.filter(
        (Transaction.from_account.in_(account_numbers)) |
        (Transaction.to_account.in_(account_numbers))
    ).order_by(Transaction.timestamp.desc()).all()
    return render_template("dashboard.html", accounts=accounts, transactions=transactions)

