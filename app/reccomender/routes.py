# app/recommender/routes.py

from flask import Blueprint, jsonify, g, request
from ..services.firebase import token_required
from database.db_helper import connect_to_db, close_connection
from ..reccomender.content_filter import ContentFilter

# Create a Blueprint for the recommender
recommender_bp = Blueprint('recommender_bp', __name__)

@recommender_bp.route('/protected', methods=['GET'])
@token_required
def protected_resource():
    # Return a success message with the user's identity
    return jsonify(
        message="You have accessed a protected resource!",
        user_id=g.current_user.id
    ), 200

@recommender_bp.route('/content-recommendations', methods=['GET'])
@token_required
def get_content_recommendations():
    """Get content-based recommendations for the current user"""
    try:
        user_id = g.current_user.id
        
        # Initialize content filter for this user
        content_filter = ContentFilter(user_id)
        
        # Get 10 recommendations
        recommended_anime_ids = content_filter.get_recommendations(user_id, 10)
        
        # Get anime details for the recommended IDs
        conn = connect_to_db()
        cursor = conn.cursor()
        
        if recommended_anime_ids:
            # Create placeholders for the IN clause
            placeholders = ','.join(['%s'] * len(recommended_anime_ids))
            query = f"""
                SELECT mal_id, title, synopsis, score, popularity 
                FROM anime_data.anime 
                WHERE mal_id IN ({placeholders})
                ORDER BY title
            """
            cursor.execute(query, recommended_anime_ids)
        else:
            cursor.execute("SELECT mal_id, title, synopsis, score, popularity FROM anime_data.anime WHERE mal_id IN (1, 21, 30) ORDER BY title")
        
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'mal_id': row[0],
                'title': row[1],
                'synopsis': row[2],
                'score': row[3],
                'popularity': row[4]
            })
        
        close_connection(conn)
        
        return jsonify({
            'recommendations': [anime['mal_id'] for anime in recommendations],
            'anime_details': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error generating recommendations: {str(e)}'
        }), 500
