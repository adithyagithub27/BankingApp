from app import db
from app.models import FixedDeposit

def calculate_maturity(amount, duration, interest_rate=5.0):
    return amount * (1 + (interest_rate / 100) * duration)

def create_fixed_deposit(user_id, amount, duration, interest_rate=5.0):
    maturity_amount = calculate_maturity(amount, duration, interest_rate)
    new_fd = FixedDeposit(
        user_id=user_id,
        amount=amount,
        duration=duration,
        interest_rate=interest_rate,
        maturity_amount=maturity_amount,
        status="Active"
    )
    db.session.add(new_fd)
    db.session.commit()
    return new_fd

def get_fixed_deposits(user_id):
    return FixedDeposit.query.filter_by(user_id=user_id).all()

def update_fixed_deposit(user_id, fd_id, amount=None, duration=None):
    """
    Update a fixed deposit instance for a given user.
    """
    fd = FixedDeposit.query.filter_by(id=fd_id, user_id=user_id).first()
    if not fd:
        return None
    if amount is not None:
        fd.amount = amount
    if duration is not None:
        fd.duration = duration
    # Recalculate the maturity amount using the current interest rate
    fd.maturity_amount = calculate_maturity(fd.amount, fd.duration, fd.interest_rate)
    db.session.commit()
    return fd

def delete_fixed_deposit(user_id, fd_id):
    """
    Delete a fixed deposit instance for a given user.
    """
    fd = FixedDeposit.query.filter_by(id=fd_id, user_id=user_id).first()
    if not fd:
        return False
    db.session.delete(fd)
    db.session.commit()
    return True

def close_fixed_deposit(user_id, fd_id):
    """
    Mark a fixed deposit as closed for a given user.
    """
    fd = FixedDeposit.query.filter_by(id=fd_id, user_id=user_id, status="Active").first()
    if not fd:
        return None
    fd.status = "Closed"
    db.session.commit()
    return fd
