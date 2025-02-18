# app/fixeddeposit.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import FixedDeposit
from app import db

fixeddeposit_bp = Blueprint("fixeddeposit", __name__)

@fixeddeposit_bp.route("/fixeddeposit", methods=["GET", "POST"])
@login_required
def fixeddeposit():
    if request.method == "POST":
        amount = float(request.form.get("fd_amount"))
        duration = float(request.form.get("fd_duration"))
        interest_rate = 5.0  # This could be dynamic based on bank policy
        # Simple interest calculation:
        maturity_amount = amount * (1 + (interest_rate/100) * duration)
        new_fd = FixedDeposit(user_id=current_user.id, amount=amount, duration=duration,
                              interest_rate=interest_rate, maturity_amount=maturity_amount)
        db.session.add(new_fd)
        db.session.commit()
        flash("Fixed deposit created successfully.", "success")
        return redirect(url_for("fixeddeposit.fixeddeposit"))
    # For GET, retrieve FD history for the current user.
    fds = FixedDeposit.query.filter_by(user_id=current_user.id).all()
    return render_template("fixeddeposit.html", fixed_deposits=fds)
