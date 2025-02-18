# app/dashboard.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Dummy data for example purposes
    accounts = [{"accountNumber": "123456789", "balance": 5000.00, "status": "Active"}]
    transactions = [
        {"date": "2023-01-15", "description": "Deposit", "amount": 200.00, "status": "Completed"},
        {"date": "2023-01-16", "description": "Withdrawal", "amount": 50.00, "status": "Completed"}
    ]
    return render_template("dashboard.html", accounts=accounts, transactions=transactions)
