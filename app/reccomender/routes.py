# app/recommender/routes.py

from flask import Blueprint, jsonify
from ..services.firebase import token_required

# Create a Blueprint for the recommender
recommender_bp = Blueprint('recommender_bp', __name__)

@recommender_bp.route('/protected', methods=['GET'])
@token_required
def protected_resource():
    # Return a success message with the user's identity
    return jsonify(
        message="You have accessed a protected resource!",
        user_id=current_user_id
    ), 200

@recommender_bp.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations():
    """
    A placeholder for a future recommendations endpoint.
    Also protected by JWT.
    """
    current_user_id = get_jwt_identity()
    
    # In the future, you would have logic here to generate recommendations
    # For now, we'll just return some dummy data.
    dummy_recommendations = [
        {"anime_id": 1, "title": "Cowboy Bebop", "score": 9.5},
        {"anime_id": 2, "title": "Attack on Titan", "score": 9.2},
        {"anime_id": 3, "title": "Steins;Gate", "score": 9.1}
    ]
    
    return jsonify(
        user_id=current_user_id,
        recommendations=dummy_recommendations
    ), 200