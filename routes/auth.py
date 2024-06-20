from flask import Blueprint, request, jsonify
from models import create_user, bcrypt, mongo

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def add_user():
    data = request.get_json()
    username = data.get("username")
    role = data.get("role")
    password = data.get("password")

    if not username or not role or not password:
        return jsonify({"error": "Missing username, role or password"}), 400

    new_user = create_user(username, role, password)

    result = {
        "_id": str(new_user["_id"]),
        "username": new_user["username"],
        "role": new_user["role"],
        "password": new_user["password"],
    }

    return jsonify(result), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    user = mongo.db.users.find_one({"username": username})

    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": f"Login successful", "role": user["role"]})
