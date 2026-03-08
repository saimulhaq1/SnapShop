from app.extensions import db
from datetime import datetime

class Brand(db.Model):
    __tablename__ = 'brand'
    
    brand_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', back_populates='brand', lazy=True)

    def __repr__(self):
        return f'<Brand {self.brand_name}>'
