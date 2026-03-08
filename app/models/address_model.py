from app.extensions import db
from .enums import CommonStatus

class Address(db.Model):
    __tablename__ = 'address'
    __table_args__ = {'extend_existing': True} 

    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    zip_code_id = db.Column(db.Integer, db.ForeignKey('zip_code.zip_code_id'), nullable=False)
    address_title = db.Column(db.String(100), nullable=False, server_default='General')
    address = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(CommonStatus, name='common_status_enum'), default=CommonStatus.ACTIVE)

    # FIXED: Added explicit overlaps and back_populates
    # We include 'customer' and 'addresses' in overlaps to cover all possible conflicting names
    customer_link = db.relationship(
        'Customer', 
        back_populates='addresses', 
        overlaps="customer,addresses,customer_link"
    )
    
    # FIXED: Added explicit overlaps for zip_code
    zip_link = db.relationship(
        'ZipCode', 
        back_populates='addresses', 
        overlaps="zip_code,addresses,zip_link"
    )
    
    # This matches the 'address_link' name in SalesOrder
    orders = db.relationship('SalesOrder', back_populates='address_link')

    def __repr__(self):
        return f"<Address {self.address_title}>"