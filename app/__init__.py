import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import timedelta
from .extensions import db
from .config import Config
from .services.firebase import token_required
from database.db_helper import connect_to_db, close_connection

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

    from .ratings.routes import ratings_bp
    app.register_blueprint(ratings_bp, url_prefix='/ratings')

    # Add anime endpoint directly to app
    @app.route('/anime', methods=['GET', 'OPTIONS'])
    @token_required
    def get_anime():
        """Get all anime with their details"""
        # Handle OPTIONS preflight request
        if request.method == 'OPTIONS':
            return '', 200
            
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT mal_id, title, synopsis, score, popularity FROM anime_data.anime ORDER BY title")
        
        # Convert to list of dictionaries for better frontend handling
        anime_list = []
        for row in cursor.fetchall():
            anime_list.append({
                'mal_id': row[0],
                'title': row[1],
                'synopsis': row[2],
                'score': row[3],
                'popularity': row[4]
            })
        
        close_connection(conn)
        return jsonify({'anime': anime_list}), 200

    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app