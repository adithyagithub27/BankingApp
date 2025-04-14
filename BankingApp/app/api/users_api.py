from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models import User

users_api_bp = Blueprint('users_api', __name__)

@users_api_bp.route('/api/users', methods=['GET'])
@login_required
def get_all_users():
    """
    Retrieve all users
    ---
    tags:
      - Users
    summary: Get all users
    description: Retrieve all user records.
    responses:
      200:
        description: A list of user records.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              username:
                type: string
                example: "john_doe"
              email:
                type: string
                example: "john@example.com"
              first_name:
                type: string
                example: "John"
              last_name:
                type: string
                example: "Doe"
              role:
                type: string
                example: "customer"
      401:
        description: Unauthorized
    """
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        })
    return jsonify(users_list)

@users_api_bp.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_by_id(user_id):
    """
    Retrieve user information by ID
    ---
    tags:
      - Users
    summary: Get user by ID
    description: Retrieve a user record by its ID.
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to retrieve.
    responses:
      200:
        description: A user record.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              example: "john@example.com"
            first_name:
              type: string
              example: "John"
            last_name:
              type: string
              example: "Doe"
            role:
              type: string
              example: "customer"
      404:
        description: User not found.
      401:
        description: Unauthorized
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    }
    return jsonify(user_data)
