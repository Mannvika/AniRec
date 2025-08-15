from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)

    ratings = db.relationship('Rating', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, firebase_id):
        self.firebase_uid = firebase_id