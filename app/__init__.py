import os
from flask import Flask
from datetime import timedelta
from .extensions import db, bcrypt, jwt

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    # TO DO

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .profile.routes import profile_bp
    app.register_blueprint(profile_bp, url_prefix='/users')

    from .reccomender.routes import recommender_bp
    app.register_blueprint(recommender_bp, url_prefix='/recommender')

    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app