from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)

    ratings = db.relationship('Rating', back_populates='user', lazy=True, cascade="all, delete-orphan")
    
    __table_args__ = {'schema': 'anime_data'}

    def __init__(self, firebase_uid, username=None):
        self.firebase_uid = firebase_uid
        # For auto-created users during login, use a temporary username
        if username:
            self.username = username
        else:
            # Generate a temporary username based on firebase_uid
            self.username = f"user_{firebase_uid[:8]}"