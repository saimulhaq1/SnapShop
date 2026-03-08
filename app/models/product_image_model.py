from datetime import datetime
from app.extensions import db

class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.pro_id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProductImage {self.id} for Product {self.product_id}>"
