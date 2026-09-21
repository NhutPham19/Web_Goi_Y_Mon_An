"""
app/utils/response.py
Helper functions để chuẩn hoá định dạng JSON response.
Mọi endpoint phải dùng các hàm này — không return dict thô.
"""
from flask import jsonify
import math


def success_response(data=None, message="OK", status_code=200):
    """
    Response thành công — single item hoặc operation.
    
    Response format:
    {
        "success": true,
        "data": { ... },
        "message": "OK"
    }
    """
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    if message and message != "OK":
        payload["message"] = message
    elif message == "OK" and status_code == 200:
        pass  # Không thêm message "OK" vào mọi response cho gọn
    else:
        payload["message"] = message
    return jsonify(payload), status_code


def paginated_response(data, total, page, limit):
    """
    Response danh sách có phân trang.
    
    Response format:
    {
        "success": true,
        "data": [...],
        "pagination": {
            "page": 1,
            "limit": 12,
            "total": 85,
            "total_pages": 8
        }
    }
    """
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    return jsonify({
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        },
    }), 200


def error_response(message, status_code=400):
    """
    Response lỗi.
    
    Response format:
    {
        "success": false,
        "error": "Mô tả lỗi",
        "code": 400
    }
    """
    return jsonify({
        "success": False,
        "error": message,
        "code": status_code,
    }), status_code
