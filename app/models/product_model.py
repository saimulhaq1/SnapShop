from datetime import datetime
from decimal import Decimal
from app.extensions import db
from .enums import ProductStatus

class Product(db.Model):
    __tablename__ = 'product'
    pro_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False, index=True) 
    barcode = db.Column(db.String(100), unique=True, nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255), nullable=True, default='default_product.png')
    buy_price = db.Column(db.Numeric(10, 2), default=0)
    sale_price = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(5, 2), default=0) # Product-level percentage
    
    cat_id = db.Column(db.Integer, db.ForeignKey('category.cat_id'), nullable=False)
    tax_id = db.Column(db.Integer, db.ForeignKey('tax_rate.tax_id'), nullable=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.brand_id'), nullable=True)

    # --- Shipping / Delivery ---
    is_free_delivery = db.Column(db.Boolean, default=True, nullable=False)
    delivery_charge = db.Column(db.Numeric(10, 2), default=0)

    status = db.Column(db.Enum(ProductStatus), default=ProductStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # REMOVED: onupdate=datetime.utcnow to prevent session conflicts during status updates
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    category = db.relationship('Category', backref='products')
    tax_rule = db.relationship('TaxRate', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
    additional_images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy=True)

    # --- MVC Logic: Smart Model Methods ---

    def get_price_plus_tax(self):
        """Calculates Base Sale Price + Tax (ignores discounts). Used for showing 'original' price."""
        base = Decimal(str(self.sale_price or 0))
        rate = Decimal(str(self.tax_rule.rate if self.tax_rule else 0))
        return base * (Decimal('1') + (rate / Decimal('100')))

    def get_total_discount_percentage(self):
        """Combines Product discount and Category discount into one total percentage."""
        prod_disc = Decimal(str(self.discount or 0))
        cat_disc = Decimal(str(self.category.discount or 0)) if self.category else Decimal('0')
        return prod_disc + cat_disc

    def get_final_price_plus_tax(self):
        """Calculates final customer price: (Base - Combined Discounts) + Tax on the discounted amount."""
        base = Decimal(str(self.sale_price or 0))
        total_disc_pc = self.get_total_discount_percentage()
        discount_amount = base * (total_disc_pc / Decimal('100'))
        discounted_base = base - discount_amount
        rate = Decimal(str(self.tax_rule.rate if self.tax_rule else 0))
        return discounted_base * (Decimal('1') + (rate / Decimal('100')))

    def adjust_stock(self, quantity):
        """Reduces stock and automatically updates status if it hits zero."""
        if self.stock < quantity:
            raise ValueError(f"Insufficient stock for {self.name}. Available: {self.stock}")
        self.stock -= quantity
        if self.stock <= 0:
            self.status = ProductStatus.OUT_OF_STOCK
        db.session.add(self)

    def restore_stock(self, quantity):
        """Adds stock back into inventory (e.g., upon an order return)."""
        self.stock += quantity
        if self.stock > 0:
            self.status = ProductStatus.ACTIVE
        db.session.add(self)

    # --- Pillar 7: Dynamic Trust Badges ---
    
    @property
    def is_new_arrival(self):
        """Returns True if the product was created within the last 7 days."""
        from datetime import timedelta
        if not self.created_at:
            return False
        return datetime.utcnow() - self.created_at <= timedelta(days=7)
        
    @property
    def is_low_stock(self):
        """Returns True if stock is between 1 and 5 inclusive."""
        return 0 < self.stock <= 5
        
    @property
    def is_best_seller(self):
        """Returns True if this product has sold more than 50 total units historically."""
        from sqlalchemy import func
        from app.models.sales_order_item_model import SalesOrderItem
        
        # Calculate total quantity sold
        total_sold = db.session.query(func.sum(SalesOrderItem.quantity))\
            .filter(SalesOrderItem.pro_id == self.pro_id)\
            .scalar() or 0
            
        return total_sold >= 50

    def __repr__(self):
        return f"<Product {self.name}>"