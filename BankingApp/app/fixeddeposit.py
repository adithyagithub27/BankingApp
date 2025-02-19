# app/fixeddeposit.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import FixedDeposit
from app import db

fixeddeposit_bp = Blueprint("fixeddeposit", __name__)

@fixeddeposit_bp.route("/", methods=["GET", "POST"])
@login_required
def fixeddeposit():
    calculated_maturity = None
    interest_rate = 5.0  # Fixed interest rate, could also come from config
    
    if request.method == "POST":
        try:
            amount = float(request.form.get("fd_amount", 0))
            duration = float(request.form.get("fd_duration", 0))
        except ValueError:
            flash("Invalid input for amount or duration.", "danger")
            return redirect(url_for("fixeddeposit.fixeddeposit"))
        
        calculated_maturity = amount * (1 + (interest_rate / 100) * duration)
        
        if "calculate" in request.form:
            flash("Interest calculated. Please review the details.", "info")
        elif "open" in request.form:
            new_fd = FixedDeposit(
                user_id=current_user.id,
                amount=amount,
                duration=duration,
                interest_rate=interest_rate,
                maturity_amount=calculated_maturity,
                status="Active"
            )
            db.session.add(new_fd)
            db.session.commit()
            flash("Fixed deposit opened successfully.", "success")
            return redirect(url_for("fixeddeposit.fixeddeposit"))
    
    fixed_deposits = FixedDeposit.query.filter_by(user_id=current_user.id).all()
    return render_template("fixeddeposit.html", fixed_deposits=fixed_deposits, calculated_maturity=calculated_maturity)

# Define the close fixed deposit route with an explicit endpoint name.
@fixeddeposit_bp.route("/close/<int:fd_id>", methods=["POST"], endpoint="close_fixeddeposit")
@login_required
def close_fixeddeposit(fd_id):
    fd = FixedDeposit.query.filter_by(id=fd_id, user_id=current_user.id, status="Active").first()
    if not fd:
        flash("Fixed deposit not found or already closed.", "danger")
        return redirect(url_for("fixeddeposit.fixeddeposit"))
    
    fd.status = "Closed"
    db.session.commit()
    flash("Fixed deposit closed successfully.", "success")
    return redirect(url_for("fixeddeposit.fixeddeposit"))
