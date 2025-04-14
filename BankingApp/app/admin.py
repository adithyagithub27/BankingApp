# app/admin.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

admin_bp = Blueprint("admin", __name__)

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    customers = User.query.filter_by(role="customer").all()
    return render_template("admin_dashboard.html", customers=customers)

@admin_bp.route("/customers/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_customer():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
            role="customer"
        )
        db.session.add(new_user)
        db.session.commit()

         # Optionally create a default account if your system requires one
        from app.models import Account
        default_account = Account(
            account_number="ACC" + str(new_user.id).zfill(8),  # e.g., ACC00000001
            balance=1000.0,  # set initial balance as desired
            user_id=new_user.id
        )
        db.session.add(default_account)
        db.session.commit()
        
        flash("Customer added successfully.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    # Return a dedicated "add_customer.html" form template
    return render_template("add_customer.html")


@admin_bp.route("/customers/delete/<int:customer_id>", methods=["POST"])
@login_required
@admin_required
def delete_customer(customer_id):
    customer = User.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/customers/delete_multiple", methods=["POST"])
def delete_multiple_users():
    selected_ids = request.form.getlist('selected_users')
    if not selected_ids:
        flash("No users selected.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    from app.models import User, Account
    for user_id in selected_ids:
        user = User.query.get(user_id)
        if user:
            # Manually delete all accounts first
            for acc in user.accounts:
                db.session.delete(acc)
            db.session.delete(user)

    db.session.commit()
    flash("Selected users have been deleted.", "success")
    return redirect(url_for("admin.admin_dashboard"))
