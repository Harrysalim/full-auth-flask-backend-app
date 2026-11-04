from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

def _json_body():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None
    return body

@auth_bp.post("/signup")
def signup():
    data = _json_body()
    if data is None:
        return jsonify(error="Request body must be valid JSON."), 400
    
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify(error="A non-empty username is required."), 400
    if len(username.strip()) > 80:
        return jsonify(error="Username must be 80 characters or fewer."), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify(error="Password must be at least 8 characters long."), 400
    if len(password) > 72:
        return jsonify(error="Password must be 72 characters or fewer."), 400

    normalized_username = username.strip()
    if User.query.filter_by(username=normalized_username).first():
        return jsonify(error="Username is already taken"), 409
    
    user = User(username=normalized_username)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Username is already taken."), 409

    
    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify(user=user.to_dict()), 201

@auth_bp.post("/login")
def login():
    data = _json_body()
    if data is None:
        return jsonify(error="Request body must be valid JSON"), 400
    
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify(error="Username and password are required."), 400
    
    user = User.query.filter_by(username=username.strip()).first()
    if user is None or not user.check_password(password):
        return jsonify(error="Invalid username or password."), 401

    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify(user=user.to_dict()), 200

@auth_bp.post("/logout")
def logout:
    session.clear()
    return jsonify(message="Logged out successfully"), 200

@auth_bp.get("/check_session")
def check_session():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify(error="Not authenticated."), 401

    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
        return jsonify(error="Not authenticated."), 401

    return jsonify(user=user.to_dict()), 200