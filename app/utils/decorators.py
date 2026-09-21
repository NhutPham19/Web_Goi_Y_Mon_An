"""
app/utils/decorators.py
Decorators dùng trong routes:
  @jwt_required_custom  — yêu cầu JWT hợp lệ
  @admin_required       — yêu cầu JWT hợp lệ + role == 'admin'
"""
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.response import error_response


def jwt_required_custom(f):
    """
    Decorator bảo vệ endpoint — yêu cầu JWT hợp lệ trong header.
    Inject current_user_id vào kwargs để route dùng.
    
    Dùng: @jwt_required_custom
    Lấy user: get_jwt_identity()
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return error_response(f"Token không hợp lệ hoặc đã hết hạn: {str(e)}", 401)
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """
    Decorator bảo vệ endpoint — yêu cầu JWT hợp lệ VÀ role == 'admin'.
    
    Dùng: @admin_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return error_response(f"Token không hợp lệ hoặc đã hết hạn: {str(e)}", 401)

        user_id = get_jwt_identity()
        from app.models.user import User
        user = User.query.get(user_id)

        if not user:
            return error_response("User không tồn tại", 401)
        if user.role != "admin":
            return error_response("Bạn không có quyền truy cập tính năng này", 403)

        return f(*args, **kwargs)
    return decorated
