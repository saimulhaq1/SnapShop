from enum import Enum

class CommonStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    BLOCKED = 'BLOCKED'

class UserRole(Enum):
    CUSTOMER = 'CUSTOMER'
    ADMIN = 'ADMIN'
    STAFF = 'STAFF'

class OrderStatus(Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'

class ProductStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    ARCHIVED = 'ARCHIVED'
    OUT_OF_STOCK = 'OUT_OF_STOCK'

class PaymentStatus(Enum):
    UNPAID = 'UNPAID'
    PARTIAL = 'PARTIAL'
    PAID = 'PAID'
    REFUNDED = 'REFUNDED'
    FAILED = 'FAILED'