from flask import Blueprint, jsonify, g, request
from app import db
from app.services.firebase import token_required
from app.models.user import User 

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/sync', methods=['POST'])
@token_required 
def sync_user():
    """
    Receives extra user data (like username) from the frontend
    immediately after a new user signs up with Firebase.
    """
    user = g.current_user
    
    if user.username:
        return jsonify({"message": "User profile already synced."}), 200

    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Username is required."}), 400

    username = data['username']

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken."}), 409
    
    user.username = username
    db.session.commit()
    
    print(f"Synced username '{username}' for user ID: {user.id}")
    
    return jsonify({
        "message": "User profile synced successfully!",
        "user": {
            "id": user.id,
            "firebase_uid": user.firebase_uid,
            "username": user.username
        }
    }), 201