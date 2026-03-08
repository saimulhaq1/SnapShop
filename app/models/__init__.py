# app/models/__init__.py

# 1. Import the db instance from your app factory/package
from app import db 

# 2. Import Enums
from .enums import CommonStatus, UserRole, OrderStatus, ProductStatus, PaymentStatus

# 3. Import individual model files
from .country_model import Country
from .state_model import State
from .city_model import City
from .zip_code_model import ZipCode
from .customer_model import Customer
from .address_model import Address
from .product_model import Product
from .category_model import Category
from .brand_model import Brand
from .taxrate_model import TaxRate
from .sales_order_model import SalesOrder
from .sales_order_item_model import SalesOrderItem
from .payment_model import Payment, PaymentMethod
from .cart_model import Cart
from .review_model import ProductReview
from .vote_tracking_model import VoteTracking
from .voucher_model import Voucher, VoucherUsage
from .banner_model import Banner
from .product_image_model import ProductImage
from .voucher_model import Voucher, VoucherUsage
from .banner_model import Banner
from .notification_model import Notification

__all__ = [
    'db',  
    'CommonStatus', 'UserRole', 'OrderStatus', 'ProductStatus', 'PaymentStatus',
    'Country', 'State', 'City', 'ZipCode',
    'Customer', 'Address',
    'Category', 'Product', 'ProductImage', 'Brand', 'TaxRate',
    'SalesOrder', 'SalesOrderItem', 'PaymentMethod', 'Payment', 'Cart',
    'ProductReview', 'VoteTracking', 'Voucher', 'VoucherUsage', 'Banner',
    'Notification'
]