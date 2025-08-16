import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify, g, make_response



try:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"🔥 Error initializing Firebase Admin SDK: {e}")


def token_required(f):

    """
    A decorator to verify the Firebase ID token.
    - Extracts token from 'Authorization: Bearer <token>' header.
    - Verifies the token with Firebase.
    - Checks if the user exists in the local DB. If not, creates them.
    - Attaches the local user object to Flask's global 'g' object.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
            return response

        from app import db 
        from app.models.user import User

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header is missing or invalid"}), 401

        id_token = auth_header.split('Bearer ')[1]
        if not id_token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Verify the token against the Firebase Auth API
            decoded_token = auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']

            # Find or create user in local database
            user = User.query.filter_by(firebase_uid=firebase_uid).first()

            if not user:
                # User exists in Firebase but not in our DB; create them.
                print(f"Creating new user for firebase_uid: {firebase_uid}")
                user = User(firebase_uid=firebase_uid)
                db.session.add(user)
                db.session.commit()

            # Attach the user object to the request context
            g.current_user = user

        except auth.ExpiredIdTokenError:
            return jsonify({"error": "Token has expired"}), 401
        except auth.InvalidIdTokenError as e:
            return jsonify({"error": "Token is invalid", "details": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

        return f(*args, **kwargs)

    return decorated_function