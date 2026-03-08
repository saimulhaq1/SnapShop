from datetime import datetime
from app.extensions import db


class VoteTracking(db.Model):
    __tablename__ = 'vote_tracking'
    __table_args__ = (
        # Ensures one user can only vote once per review
        db.UniqueConstraint('review_id', 'customer_id', name='uq_vote_per_user'),
        {'extend_existing': True}
    )

    vote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('product_review.review_id', ondelete='CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id', ondelete='CASCADE'), nullable=False)

    # 'like' or 'dislike'
    vote_type = db.Column(db.Enum('like', 'dislike', name='vote_type_enum'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    review = db.relationship('ProductReview', back_populates='votes')
    voter = db.relationship('Customer', foreign_keys=[customer_id])

    def __repr__(self):
        return f'<VoteTracking review={self.review_id} user={self.customer_id} type={self.vote_type}>'
