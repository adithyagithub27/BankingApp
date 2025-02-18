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
        password = generate_password_hash(request.form.get("password"))
        new_user = User(first_name=first_name, last_name=last_name,
                        email=email, username=username, password=password, role="customer")
        db.session.add(new_user)
        db.session.commit()
        flash("Customer added successfully.", "success")
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("admin_dashboard.html", add_customer=True)

@admin_bp.route("/customers/delete/<int:customer_id>", methods=["POST"])
@login_required
@admin_required
def delete_customer(customer_id):
    customer = User.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))
