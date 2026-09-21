"""
app.py — Entry point
Chạy local: flask run  hoặc  python app.py
Chạy production: gunicorn app:app  (Procfile)
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
