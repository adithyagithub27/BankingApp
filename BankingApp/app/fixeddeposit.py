from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services import (
    calculate_maturity, 
    create_fixed_deposit, 
    get_fixed_deposits, 
    update_fixed_deposit, 
    delete_fixed_deposit, 
    close_fixed_deposit
)
from app.models import FixedDeposit
from app import db

# Define blueprint with a URL prefix so endpoints are registered as fixeddeposit.* 
fixeddeposit_bp = Blueprint("fixeddeposit", __name__, url_prefix="/fixeddeposit")

# ---------------------------
# HTML Endpoint for Fixed Deposit Operations
# ---------------------------
@fixeddeposit_bp.route("/", methods=["GET", "POST"])
@login_required
def fixeddeposit():
    calculated_maturity = None
    interest_rate = 5.0  # or retrieve from config

    if request.method == "POST":
        try:
            amount = float(request.form.get("fd_amount", 0))
            duration = float(request.form.get("fd_duration", 0))
        except ValueError:
            flash("Invalid input for amount or duration.", "danger")
            return redirect(url_for("fixeddeposit.fixeddeposit"))
        
        calculated_maturity = calculate_maturity(amount, duration, interest_rate)
        
        if "calculate" in request.form:
            flash("Interest calculated. Please review the details.", "info")
        elif "open" in request.form:
            # For HTML, use the authenticated user (current_user.id)
            create_fixed_deposit(current_user.id, amount, duration, interest_rate)
            flash("Fixed deposit opened successfully.", "success")
            return redirect(url_for("fixeddeposit.fixeddeposit"))
    
    deposits = get_fixed_deposits(current_user.id)
    return render_template("fixeddeposit.html", fixed_deposits=deposits, calculated_maturity=calculated_maturity)

# ---------------------------
# HTML Endpoint for Closing a Fixed Deposit
# ---------------------------
@fixeddeposit_bp.route("/close/<int:fd_id>", methods=["POST"], endpoint="close_fixeddeposit")
@login_required
def close_fixeddeposit(fd_id):
    # Fetch the fixed deposit record using current_user.id
    fd = FixedDeposit.query.filter_by(id=fd_id, user_id=current_user.id, status="Active").first()
    if not fd:
        flash("Fixed deposit not found or already closed.", "danger")
        return redirect(url_for("fixeddeposit.fixeddeposit"))
    fd.status = "Closed"
    db.session.commit()
    flash("Fixed deposit closed successfully.", "success")
    return redirect(url_for("fixeddeposit.fixeddeposit"))

# ----------------------------------------------------------
# API Endpoint for Collection Operations (/api/fixeddeposits)
# ----------------------------------------------------------
@fixeddeposit_bp.route("/api/fixeddeposits", methods=["GET", "POST"])
@login_required
def fixeddeposits_api():
    """
    Fixed Deposit - List and Create Operations
    ---
    tags:
      - Fixed Deposit
    get:
      summary: List Fixed Deposits
      description: Retrieve all fixed deposits for a given user. If 'user_id' is provided as a query parameter, it will be used; otherwise, the authenticated user's ID is used.
      parameters:
        - in: query
          name: user_id
          type: integer
          required: false
          description: Optional user ID.
      responses:
        200:
          description: A list of fixed deposit records.
          schema:
            type: array
            items:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                amount:
                  type: number
                  example: 1000
                duration:
                  type: number
                  example: 2
                interest_rate:
                  type: number
                  example: 5.0
                maturity_amount:
                  type: number
                  example: 1100
                status:
                  type: string
                  example: "Active"
                created_at:
                  type: string
                  format: date-time
                  example: "2025-04-05T17:30:00"
    post:
      summary: Create or Calculate Fixed Deposit
      description: Create a new fixed deposit or calculate its maturity.
      parameters:
        - in: body
          name: fixed_deposit
          description: Fixed deposit details.
          required: true
          schema:
            type: object
            properties:
              user_id:
                type: integer
                example: 2
                description: "Optional user ID. If not provided, the authenticated user is used."
              fd_amount:
                type: number
                example: 1000
              fd_duration:
                type: number
                example: 2
              calculate:
                type: boolean
                example: false
              open:
                type: boolean
                example: true
      responses:
        200:
          description: Interest calculated.
          schema:
            type: object
            properties:
              message:
                type: string
                example: "Interest calculated."
              calculated_maturity:
                type: number
                example: 1100
        201:
          description: Fixed deposit opened successfully.
          schema:
            type: object
            properties:
              message:
                type: string
                example: "Fixed deposit opened successfully."
              calculated_maturity:
                type: number
                example: 1100
        400:
          description: Invalid input or no valid action specified.
    """
    interest_rate = 5.0
    # Retrieve user_id from query or JSON; default to current_user.id if not provided.
    user_id = request.args.get("user_id")
    if not user_id:
        data = request.get_json(silent=True) or {}
        user_id = int(data.get("user_id", current_user.id))
    else:
        user_id = int(user_id)
    
    if request.method == "GET":
        deposits = get_fixed_deposits(user_id)
        response = [{
            "id": d.id,
            "amount": d.amount,
            "duration": d.duration,
            "interest_rate": d.interest_rate,
            "maturity_amount": d.maturity_amount,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in deposits]
        return jsonify(response)
    
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"message": "Missing JSON data"}), 400
        user_id = int(data.get("user_id", current_user.id))
        try:
            amount = float(data.get("fd_amount", 0))
            duration = float(data.get("fd_duration", 0))
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid input for amount or duration."}), 400
        calculated_maturity = calculate_maturity(amount, duration, interest_rate)
        if data.get("calculate"):
            return jsonify({"message": "Interest calculated.", "calculated_maturity": calculated_maturity})
        elif data.get("open"):
            new_deposit = create_fixed_deposit(user_id, amount, duration, interest_rate)
            return jsonify({"message": "Fixed deposit opened successfully.", "calculated_maturity": new_deposit.maturity_amount}), 201
        return jsonify({"message": "No valid action specified."}), 400

# ----------------------------------------------------------
# API Endpoint for Detail Operations (/api/fixeddeposits/<fd_id>)
# ----------------------------------------------------------
@fixeddeposit_bp.route("/api/fixeddeposits/<int:fd_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def fixeddeposits_detail_api(fd_id):
    """
    Fixed Deposit - Detail, Update, and Delete Operations
    ---
    tags:
      - Fixed Deposit
    get:
      summary: Retrieve Fixed Deposit Detail
      description: Retrieve a specific fixed deposit by ID. Accepts an optional user_id query parameter.
      parameters:
        - in: path
          name: fd_id
          type: integer
          required: true
        - in: query
          name: user_id
          type: integer
          required: false
          description: Optional user ID; defaults to the authenticated user.
      responses:
        200:
          description: A fixed deposit record.
          schema:
            type: object
            properties:
              id:
                type: integer
                example: 1
              amount:
                type: number
                example: 1000
              duration:
                type: number
                example: 2
              interest_rate:
                type: number
                example: 5.0
              maturity_amount:
                type: number
                example: 1100
              status:
                type: string
                example: "Active"
              created_at:
                type: string
                format: date-time
                example: "2025-04-05T17:30:00"
        404:
          description: Fixed deposit not found.
    put:
      summary: Update Fixed Deposit
      description: Update a fixed deposit.
      parameters:
        - in: path
          name: fd_id
          type: integer
          required: true
        - in: body
          name: fixed_deposit
          description: Fixed deposit update details.
          required: true
          schema:
            type: object
            properties:
              user_id:
                type: integer
                example: 2
              fd_amount:
                type: number
                example: 1500
              fd_duration:
                type: number
                example: 3
      responses:
        200:
          description: Fixed deposit updated successfully.
        400:
          description: Invalid input.
        404:
          description: Fixed deposit not found.
    delete:
      summary: Delete Fixed Deposit
      description: Delete a fixed deposit.
      parameters:
        - in: path
          name: fd_id
          type: integer
          required: true
        - in: query
          name: user_id
          type: integer
          required: false
          description: Optional user ID; defaults to the authenticated user.
      responses:
        200:
          description: Fixed deposit deleted successfully.
        404:
          description: Fixed deposit not found.
    """
    user_id = request.args.get("user_id")
    if not user_id:
        data = request.get_json(silent=True) or {}
        user_id = int(data.get("user_id", current_user.id))
    else:
        user_id = int(user_id)
    
    deposit = FixedDeposit.query.filter_by(id=fd_id, user_id=user_id).first()
    if not deposit:
        return jsonify({"message": "Fixed deposit not found."}), 404

    if request.method == "GET":
        response = {
            "id": deposit.id,
            "amount": deposit.amount,
            "duration": deposit.duration,
            "interest_rate": deposit.interest_rate,
            "maturity_amount": deposit.maturity_amount,
            "status": deposit.status,
            "created_at": deposit.created_at.isoformat() if deposit.created_at else None
        }
        return jsonify(response)
    elif request.method == "PUT":
        data = request.get_json()
        if not data:
            return jsonify({"message": "Missing JSON data."}), 400
        user_id = int(data.get("user_id", current_user.id))
        try:
            amount = float(data.get("fd_amount", deposit.amount))
            duration = float(data.get("fd_duration", deposit.duration))
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid input for amount or duration."}), 400
        updated = update_fixed_deposit(user_id, fd_id, amount, duration)
        if updated is None:
            return jsonify({"message": "Fixed deposit not found."}), 404
        return jsonify({"message": "Fixed deposit updated successfully."})
    elif request.method == "DELETE":
        user_id = request.args.get("user_id")
        if not user_id:
            data = request.get_json(silent=True) or {}
            user_id = int(data.get("user_id", current_user.id))
        else:
            user_id = int(user_id)
        success = delete_fixed_deposit(user_id, fd_id)
        if not success:
            return jsonify({"message": "Fixed deposit not found."}), 404
        return jsonify({"message": "Fixed deposit deleted successfully."})

# ----------------------------------------------------------
# API Endpoint for Closing a Fixed Deposit (/api/fixeddeposits/close/<fd_id>)
# ----------------------------------------------------------
@fixeddeposit_bp.route("/api/fixeddeposits/close/<int:fd_id>", methods=["POST"])
@login_required
def fixeddeposits_close_api(fd_id):
    """
    Fixed Deposit - Close Operation
    ---
    tags:
      - Fixed Deposit
    post:
      summary: Close Fixed Deposit
      description: Mark a fixed deposit as closed.
      parameters:
        - in: path
          name: fd_id
          type: integer
          required: true
        - in: body
          name: fixed_deposit
          description: Optional JSON payload to specify user_id.
          required: false
          schema:
            type: object
            properties:
              user_id:
                type: integer
                example: 2
      responses:
        200:
          description: Fixed deposit closed successfully.
          schema:
            type: object
            properties:
              message:
                type: string
                example: "Fixed deposit closed successfully."
        404:
          description: Fixed deposit not found or already closed.
    """
    data = request.get_json(silent=True) or {}
    user_id = int(data.get("user_id", current_user.id))
    deposit = close_fixed_deposit(user_id, fd_id)
    if not deposit:
        return jsonify({"message": "Fixed deposit not found or already closed."}), 404
    return jsonify({"message": "Fixed deposit closed successfully."})
