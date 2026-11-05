import os

from flask import Flask, jsonify, request
from sqlalchemy import inspect

from config import Config
from extensions import bcrypt, db, migrate
from routes.auth import auth_bp
from routes.notes import notes_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.setdefault("MAX_PER_PAGE", 100)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from models import Note, User

    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    @app.get("/")
    def home():
        return jsonify(
            message="Productivity Notes API",
            endpoints={
                "signup": "POST /signup",
                "login": "POST /login",
                "logout": "POST /logout",
                "check_session": "GET /check_session",
                "notes": "GET, POST /notes",
                "note": "GET, PATCH, DELETE /notes/<id>",

            },
        ),  200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error="Endpoint not Found."), 404
    
    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify(error="Method not allowed."), 405
    
    @app.after_request
    def add_cors_header(response):
        allowed_origin = os.environ.get("FRONTEND_ORIGIN")
        origin = request.headers.get("Origin")
        if allowed_origin and origin == allowed_origin:
            response.headers["Access-Control-Allowed-Origin"] = allowed_origin
            response.headers["Access-Control-Allowed-Credentials"] = "true"
            response.headers["Access-Control-Allowed-Headers"] = "Content-Type"
            response.headers["Access-Control-Allowed-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
            response.headers.add("Vary", "Origin")
        return response
    
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return ("", 204)
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)