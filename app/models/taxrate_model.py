from app.extensions import db
from .enums import CommonStatus

class TaxRate(db.Model):
    __tablename__ = 'tax_rate'
    tax_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    tax_name = db.Column(db.String(50), nullable=False) # e.g., GST, VAT
    rate = db.Column(db.Numeric(5, 2), nullable=False)   # e.g., 15.00
    status = db.Column(db.Enum(CommonStatus), default=CommonStatus.ACTIVE)

    # --- Relationships ---
    # MVC Update: Connects back to Product.tax_rule to solve the ArgumentError
    products = db.relationship('Product', back_populates='tax_rule')

    def __repr__(self):
        return f"<TaxRate {self.tax_name} ({self.rate}%)>"