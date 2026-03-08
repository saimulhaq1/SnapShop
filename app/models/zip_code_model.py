from app.extensions import db
from .enums import CommonStatus

class ZipCode(db.Model):
    __tablename__ = 'zip_code'
    zip_code_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zip_code_name = db.Column(db.String(20), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable=False)
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)
    
    addresses = db.relationship('Address', backref='zip_code', lazy=True)