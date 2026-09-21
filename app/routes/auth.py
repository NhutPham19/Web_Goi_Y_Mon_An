"""
app/routes/auth.py
Blueprint: auth_bp
Endpoints:
  POST /api/auth/register
  POST /api/auth/login
  GET  /api/auth/me
  POST /api/auth/logout
"""
import re
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt_identity
import bcrypt

from app import db
from app.models.user import User, UserPreference
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required_custom

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /api/auth/register
    Body: { "email": "...", "password": "...", "full_name": "..." }
    """
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    # Validation
    if not email or not EMAIL_REGEX.match(email):
        return error_response("Email không hợp lệ", 400)
    if len(password) < 8:
        return error_response("Mật khẩu phải có ít nhất 8 ký tự", 400)
    if not full_name:
        return error_response("Vui lòng nhập họ và tên", 400)

    # Kiểm tra email đã tồn tại chưa
    if User.query.filter_by(email=email).first():
        return error_response("Email đã được đăng ký", 409)

    # Hash password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Tạo user mới
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    # Tạo JWT token
    token = create_access_token(identity=user.id)

    return success_response(
        data={"token": token, "user": user.to_dict()},
        message="Đăng ký thành công",
        status_code=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { "email": "...", "password": "..." }
    """
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error_response("Email và mật khẩu là bắt buộc", 400)

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        return error_response("Email hoặc mật khẩu không đúng", 401)

    token = create_access_token(identity=user.id)

    return success_response(
        data={"token": token, "user": user.to_dict(include_preferences=True)},
        message="Đăng nhập thành công",
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required_custom
def me():
    """
    GET /api/auth/me
    Header: Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return error_response("User không tồn tại", 404)

    return success_response(data=user.to_dict(include_preferences=True))


@auth_bp.route("/logout", methods=["POST"])
@jwt_required_custom
def logout():
    """
    POST /api/auth/logout
    Client-side: xóa token khỏi storage.
    Server-side: không cần blacklist cho dự án này.
    """
    return success_response(message="Đăng xuất thành công")


# ─── User Preferences Endpoints (gắn vào auth blueprint) ─────────────────────

@auth_bp.route("/users/me/preferences", methods=["GET"])
@jwt_required_custom
def get_preferences():
    """GET /api/auth/users/me/preferences"""
    user_id = get_jwt_identity()
    prefs = UserPreference.query.filter_by(user_id=user_id).all()
    return success_response(data=[p.to_dict() for p in prefs])


@auth_bp.route("/users/me/preferences", methods=["POST"])
@jwt_required_custom
def set_preferences():
    """
    POST /api/auth/users/me/preferences
    Body: { "preferences": [{"pref_type": "diet", "pref_value": "vegetarian"}, ...] }
    Upsert: xóa cũ, insert batch mới.
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    preferences = data.get("preferences", [])

    if not isinstance(preferences, list):
        return error_response("preferences phải là mảng", 400)

    # Xóa preferences cũ
    UserPreference.query.filter_by(user_id=user_id).delete()

    # Insert batch mới
    for pref in preferences:
        pref_type = pref.get("pref_type", "").strip()
        pref_value = pref.get("pref_value", "").strip()

        if pref_type and pref_value:
            db.session.add(UserPreference(
                user_id=user_id,
                pref_type=pref_type,
                pref_value=pref_value,
            ))

    db.session.commit()

    updated_prefs = UserPreference.query.filter_by(user_id=user_id).all()
    return success_response(
        data=[p.to_dict() for p in updated_prefs],
        message="Cập nhật sở thích thành công",
    )
