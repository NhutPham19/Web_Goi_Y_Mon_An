"""
app/__init__.py — App Factory Pattern
Tạo Flask app, đăng ký extensions, blueprints.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Extensions — khởi tạo không bind app (pattern factory)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config=None):
    """
    Factory function tạo Flask app.
    Dùng: app = create_app()
    """
    app = Flask(__name__)

    # Load config
    if config is None:
        from config import get_config
        app.config.from_object(get_config())
    else:
        app.config.from_object(config)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS — cho phép tất cả origin trong dev, thu hẹp ở prod
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Import models để Flask-Migrate nhận diện
    with app.app_context():
        from app.models import user, recipe, ingredient, rating, meal_plan  # noqa

    # Đăng ký blueprints
    _register_blueprints(app)

    # Health check endpoint (không cần auth)
    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "nauAn-backend"}, 200

    return app


def _register_blueprints(app):
    from app.routes.auth import auth_bp
    from app.routes.recipes import recipes_bp
    from app.routes.ingredients import ingredients_bp
    from app.routes.search import search_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.ratings import ratings_bp
    from app.routes.meal_plans import meal_plans_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp,            url_prefix="/api/auth")
    app.register_blueprint(recipes_bp,         url_prefix="/api")
    app.register_blueprint(ingredients_bp,     url_prefix="/api")
    app.register_blueprint(search_bp,          url_prefix="/api/search")
    app.register_blueprint(recommendations_bp, url_prefix="/api")
    app.register_blueprint(ratings_bp,         url_prefix="/api")
    app.register_blueprint(meal_plans_bp,      url_prefix="/api")
    app.register_blueprint(admin_bp,           url_prefix="/api/admin")
