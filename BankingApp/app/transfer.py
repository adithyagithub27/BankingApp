# app/transfer.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Transaction
from app import db

transfer_bp = Blueprint("transfer", __name__)

@transfer_bp.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        from_account = request.form.get("from_account")
        to_account = request.form.get("dest_account")
        amount = float(request.form.get("amount"))
        transfer_type = request.form.get("transfer_type")
        description = request.form.get("description")
        # Here, add your funds validation and processing logic
        # For now, we simulate a successful transaction
        new_txn = Transaction(from_account=from_account,
                              to_account=to_account,
                              amount=amount,
                              status="Completed")
        db.session.add(new_txn)
        db.session.commit()
        flash("Transfer completed successfully.", "success")
        return redirect(url_for("dashboard.dashboard"))
    return render_template("transfer.html")
