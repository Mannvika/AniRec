from flask import Blueprint, jsonify, g, request
from ..services.firebase import token_required
from ..models.anime import Rating
from ..models.user import User
from ..extensions import db

ratings_bp = Blueprint('ratings_bp', __name__)

@ratings_bp.route('/anime/<int:anime_id>', methods=['POST', 'OPTIONS'])
@token_required
def submit_or_update_rating(anime_id):
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    user = g.current_user.id

    score = request.json.get('score')
    if score is None:
        return jsonify({"message": "Score is required"}), 400
    
    existing_rating = Rating.query.filter_by(user_id=user, anime_id=anime_id).first()

    from ..models import Anime
    anime = Anime.query.get(anime_id)
    if not anime:
        return jsonify({"message": "Anime not found"}), 404

    if existing_rating:
        existing_rating.score = request.json.get('score')
        action = "updated"
    else:
        new_rating = Rating(user_id=user, anime_id=anime_id, score=request.json.get('score'))
        db.session.add(new_rating)
        action = "created"

    db.session.commit()
    return jsonify({"message": f"Rating {action}"}), 200

@ratings_bp.route('/anime/<int:anime_id>', methods=['GET', 'OPTIONS'])
@token_required
def get_ratings(anime_id):
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    user = g.current_user.id
    rating = Rating.query.filter_by(user_id=user, anime_id=anime_id).first()
    if not rating:
        return jsonify({"message": "Rating not found"}), 404

    return jsonify({"message": f"Rating for anime {anime_id} is {rating.score} for user {user}"}), 200

@ratings_bp.route('/ratings/delete/<int:anime_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_rating(anime_id):
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    user = g.current_user.id
    rating = Rating.query.filter_by(user_id=user, anime_id=anime_id).first()
    if not rating:
        return jsonify({"message": "Rating not found"}), 404
    db.session.delete(rating)
    db.session.commit()
    return jsonify({"message": f"Delete rating for anime {anime_id}"}), 200


