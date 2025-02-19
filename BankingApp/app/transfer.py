# app/transfer.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Account,Transaction
from app import db

transfer_bp = Blueprint("transfer", __name__)


@transfer_bp.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        from_account_id = request.form.get("from_account")
        dest_account_id = request.form.get("dest_account")
        try:
            amount = float(request.form.get("amount"))
        except ValueError:
            flash("Invalid amount.", "danger")
            return redirect(url_for("transfer.transfer"))
        
        from_account = Account.query.filter_by(id=from_account_id, user_id=current_user.id).first()
        if not from_account:
            flash("Invalid source account.", "danger")
            return redirect(url_for("transfer.transfer"))
        
        if from_account.balance < amount:
            flash("Insufficient funds.", "danger")
            return redirect(url_for("transfer.transfer"))
        
        dest_account = Account.query.filter_by(id=dest_account_id).first()
        if not dest_account or dest_account.user_id == current_user.id:
            flash("Invalid destination account.", "danger")
            return redirect(url_for("transfer.transfer"))
        
        from_account.balance -= amount
        dest_account.balance += amount
        
        new_txn = Transaction(
            from_account=from_account.account_number,
            to_account=dest_account.account_number,
            amount=amount,
            status="Completed"
        )
        db.session.add(new_txn)
        db.session.commit()
        
        flash("Transfer completed successfully.", "success")
        return redirect(url_for("dashboard.dashboard"))
    
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    dest_accounts = Account.query.filter(Account.user_id != current_user.id).all()
    return render_template("transfer.html", user_accounts=user_accounts, dest_accounts=dest_accounts)