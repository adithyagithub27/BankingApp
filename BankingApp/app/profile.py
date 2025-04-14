# app/profile.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # Retrieve form fields
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        gender = request.form.get("gender")  # 'male' or 'female' or None
        newsletter = request.form.get("newsletter")  # 'on' if checked, else None

        # Update current user
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.gender = gender  # ensure you have a 'gender' column in User model
        current_user.newsletter_subscribed = (newsletter == "on")

        db.session.commit()

        # Show a success alert
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.profile"))
    
    # GET: Display the form with current user info
    return render_template("profile.html", user=current_user)
