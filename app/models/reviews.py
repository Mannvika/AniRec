from app.extensions import db

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime_data.anime.mal_id'), nullable=False)
    review_text = db.Column(db.Text, nullable=False)

    __table_args__ = {'schema': 'anime_data'}

    def __repr__(self):
        return f'<Review {self.review_id}: {self.anime_id}>'