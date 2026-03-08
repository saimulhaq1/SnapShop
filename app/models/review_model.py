from datetime import datetime
from app.extensions import db


class ReviewPhoto(db.Model):
    __tablename__ = 'review_photo'
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('product_review.review_id', ondelete='CASCADE'), nullable=False)
    photo_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductReview(db.Model):
    __tablename__ = 'product_review'
    __table_args__ = {'extend_existing': True}

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.pro_id', ondelete='CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id', ondelete='CASCADE'), nullable=False)

    # Self-referencing FK for threaded replies (NULL = top-level review)
    parent_id = db.Column(db.Integer, db.ForeignKey('product_review.review_id', ondelete='CASCADE'), nullable=True)

    # Rating only on top-level reviews (nullable for replies)
    rating = db.Column(db.Integer, nullable=True)  # 1–5 stars; None for replies
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Pillar 7: Verified Purchase System
    verified_purchase = db.Column(db.Boolean, default=False, nullable=False)

    # --- Relationships ---
    author = db.relationship('Customer', foreign_keys=[customer_id], back_populates='reviews')
    product = db.relationship('Product', foreign_keys=[product_id], backref='reviews')
    votes = db.relationship('VoteTracking', back_populates='review', cascade='all, delete-orphan')
    photos = db.relationship('ReviewPhoto', backref='review', cascade='all, delete-orphan')

    # Self-referential: top-level review -> list of replies
    replies = db.relationship(
        'ProductReview',
        foreign_keys=[parent_id],
        backref=db.backref('parent', remote_side='ProductReview.review_id'),
        cascade='all, delete-orphan'
    )

    def like_count(self):
        return sum(1 for v in self.votes if v.vote_type == 'like')

    def dislike_count(self):
        return sum(1 for v in self.votes if v.vote_type == 'dislike')
        
    @classmethod
    def check_if_verified(cls, customer_id, product_id):
        """
        Dynamically checks if a customer has ever purchased and received a specific product.
        Used to set the verified_purchase flag when a review is created.
        """
        from app.models.sales_order_model import SalesOrder, OrderStatus
        from app.models.sales_order_item_model import SalesOrderItem
        
        # Check if an order item exists for this product, linked to a delivered order for this customer
        verified = db.session.query(SalesOrderItem).join(SalesOrder).filter(
            SalesOrder.customer_id == customer_id,
            SalesOrder.status == OrderStatus.DELIVERED,
            SalesOrderItem.pro_id == product_id
        ).first()
        
        return verified is not None

    def __repr__(self):
        return f'<ProductReview #{self.review_id} product={self.product_id} rating={self.rating}>'
