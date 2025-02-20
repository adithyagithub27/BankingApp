# app/auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import User
from app import db
from flask_login import login_user, logout_user, current_user
from flask_mail import Message
import itsdangerous
from app import mail

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route that compares the stored password (plain text) to the entered password.
    If they match exactly, the user is logged in. Otherwise, an error is displayed.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        # Direct equality check for plain-text passwords (NOT secure in production!)
        if user and user.password == password:
            login_user(user)
            flash("Logged in successfully.", "success")
            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Signup route that stores the password in plain text (NOT recommended for production).
    """
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        
        # Basic checks
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.signup"))
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("User with that username or email already exists.", "danger")
            return redirect(url_for("auth.signup"))
        
        # Store password in plain text (again, NOT secure in production)
        new_user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
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

        flash("Signup successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():
    """
    Logs out the current user and redirects to the login page.
    """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
