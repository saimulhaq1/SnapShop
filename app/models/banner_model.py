from datetime import datetime
from app.extensions import db
from .enums import CommonStatus

class Banner(db.Model):
    __tablename__ = 'banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=True) # Optional title
    image_url = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Banner {self.title or self.id}>"
