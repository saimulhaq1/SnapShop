from datetime import datetime
from app.extensions import db
from .enums import PaymentStatus

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    method_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pay_method_name = db.Column(db.String(50), nullable=False)

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.order_id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('payment_method.method_id'), nullable=False)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)
    wallet_number = db.Column(db.String(20), nullable=True)
    account_holder_name = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum(PaymentStatus, name='payment_status_new_enum'), default=PaymentStatus.UNPAID)

    method = db.relationship('PaymentMethod', backref='payments')