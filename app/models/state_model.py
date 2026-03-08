from app.extensions import db
from .enums import CommonStatus

class State(db.Model):
    __tablename__ = 'state'
    state_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)
    
    cities = db.relationship('City', backref='state', lazy=True)