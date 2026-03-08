from datetime import datetime
from app.extensions import db
from .enums import CommonStatus

class Category(db.Model):
    __tablename__ = 'category'
    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_cat_id = db.Column(db.Integer, db.ForeignKey('category.cat_id'), nullable=True)
    cat_name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True, default='default_category.png')
    discount = db.Column(db.Float, default=0.0) # Category-level percentage
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # FIXED RELATIONSHIP:
    # 1. 'subcategories' gives you a list of children: cat.subcategories
    # 2. 'parent_node' gives you the parent object: cat.parent_node
    # The 'remote_side' is only needed once on the backref to avoid the Direction error.
    subcategories = db.relationship(
        'Category', 
        backref=db.backref('parent_node', remote_side=[cat_id]),
        lazy='select'
    )

    def __repr__(self):
        return f"<Category {self.cat_name}>"