from app.extensions import db

class Anime(db.Model):
    __tablename__ = 'anime'

    mal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    synopsis = db.Column(db.Text, nullable=True)
    score = db.Column(db.Real, nullable=True)
    popularity = db.Column(db.Integer, nullable=True)
    genres = db.Column(db.ARRAY(db.Text), nullable=True)
    themes = db.Column(db.ARRAY(db.Text), nullable=True)
    demographics = db.Column(db.ARRAY(db.Text), nullable=True)
    studios = db.Column(db.ARRAY(db.Text), nullable=True)
    producers = db.Column(db.ARRAY(db.Text), nullable=True)
    
    content_string = db.Column(db.Text, nullable=True)

    ratings = db.relationship('Rating', backref='anime', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Anime {self.mal_id}: {self.title}>'

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.mal_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'anime_id', name='_user_anime_uc'),)

    def __repr__(self):
        return f'<Rating {self.id}: User {self.user_id} rated Anime {self.anime_id} with score {self.score}>'
