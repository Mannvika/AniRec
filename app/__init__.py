import os
from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from .extensions import db
from .config import Config

def create_app():
    app = Flask(__name__)
    CORS(app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        allow_headers=["Authorization", "Content-Type"],
        supports_credentials=True)    
    # Load configuration
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    from .profile.routes import profile_bp
    app.register_blueprint(profile_bp, url_prefix='/users')

    from .reccomender.routes import recommender_bp
    app.register_blueprint(recommender_bp, url_prefix='/recommender')

    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app