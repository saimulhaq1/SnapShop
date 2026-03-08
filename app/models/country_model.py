from app.extensions import db
from .enums import CommonStatus

class Country(db.Model):
    __tablename__ = 'country'
    country_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)
    
    # Relationships
    states = db.relationship('State', backref='country', lazy=True)
    tax_rates = db.relationship('TaxRate', backref='country', lazy=True)