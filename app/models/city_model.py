from app.extensions import db
from .enums import CommonStatus

class City(db.Model):
    __tablename__ = 'city'
    city_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.state_id'), nullable=False)
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)
    
    zip_codes = db.relationship('ZipCode', backref='city', lazy=True)