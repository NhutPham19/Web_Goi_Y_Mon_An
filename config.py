"""
config.py — Cấu hình ứng dụng Flask
Đọc tất cả từ biến môi trường (.env), tuyệt đối không hardcode credentials.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config — mọi môi trường đều kế thừa."""

    # Flask core
    SECRET_KEY = os.environ.get("SECRET_KEY") or "fallback-insecure-key-change-in-production"
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,          # Tự kiểm tra kết nối trước khi dùng
        "pool_recycle": 300,            # Recycle connection sau 5 phút
        "connect_args": {
            "connect_timeout": 10,
            "options": "-c timezone=UTC",
        },
    }

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

    # Pagination defaults
    DEFAULT_PAGE_SIZE = 12
    MAX_PAGE_SIZE = 50

    # Recommendation cache TTL (giây)
    RECOMMENDATION_CACHE_TTL = 3600  # 1 giờ

    # ML thresholds
    CF_MIN_RATINGS = 200  # Số ratings tối thiểu để dùng CF


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set True để xem SQL queries khi debug


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # Render tự inject PORT; gunicorn bind qua Procfile
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


# Map tên môi trường sang class config
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "production")
    return config_map.get(env, config_map["default"])
