from functools import wraps
from flask import request, flash, redirect, url_for, session, render_template
from app.models.customer_model import Customer
from app.models.enums import CommonStatus

# --- 1. THE PERMISSION DECORATOR ---
def admin_permission_required(permission_key, page_display_name):
    """
    Decorator to block access based on Admin Role Assignment.
    It reads from the session-synced permissions.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get permissions from session (synced by __init__.py)
            perms = session.get('session_user_permissions', {})
            is_admin = session.get('role') == 'ADMIN'
            
            # Logic: If the 'Hide' toggle is True in the session dictionary
            if is_admin and perms.get(permission_key):
                # Optionally use a flash message and redirect, or render the error page
                return render_template('errors/unauthorized.html', page_name=page_display_name), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- 2. GLOBAL MIDDLEWARE INIT ---
def init_middleware(flask_app):
    """
    Registers the context processor, which validates 
    session permissions on every page load and injects unread notifications.
    """
    @flask_app.context_processor
    def inject_permissions_and_notifications():
        user_id = session.get('user_id')
        role = session.get('role')
        
        # 1. PERMISSIONS - read from session (already synced by before_request)
        perms = session.get('session_user_permissions', {})
                     
        # 2. NOTIFICATIONS
        unread_notifications = []
        if user_id:
            from app.models.notification_model import Notification
            if role in ['ADMIN', 'STAFF']:
                from app import db
                from sqlalchemy import or_
                unread_notifications = Notification.query.filter(
                    Notification.is_read == False,
                    or_(
                        Notification.user_id == user_id,
                        Notification.user_id.is_(None) # global orders
                    ),
                    Notification.recipient_role == 'ADMIN'
                ).order_by(Notification.created_at.desc()).limit(15).all()
            else:
                # Customers see specific alerts or broadcasts
                from app import db
                from sqlalchemy import or_
                unread_notifications = Notification.query.filter(
                    Notification.is_read == False,
                    or_(
                        Notification.user_id == user_id,
                        Notification.user_id.is_(None) # broadcasts
                    ),
                    Notification.recipient_role == 'CUSTOMER'
                ).order_by(Notification.created_at.desc()).limit(15).all()

        return dict(
            session_user_permissions=perms,
            current_notifications=unread_notifications
        )

    @flask_app.before_request
    def check_user_status():
        """
        Check if a logged-in user's status has changed to BLOCKED.
        """
        # Exclude static files from DB checks to save performance
        if request.endpoint == 'static':
            return

        user_id = session.get('user_id')
        if user_id:
            user = Customer.query.get(user_id)
            if user and user.status == CommonStatus.BLOCKED:
                session.clear()
                flash("Your account has been blocked by an admin.", "danger")
                
                # FIXED: Changed from auth_session.login to login.login
                return redirect(url_for('login.login'))

    @flask_app.after_request
    def add_header(response):
        """
        Prevent browser caching of sensitive pages.
        """
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @flask_app.context_processor
    def inject_low_stock_alerts():
        """
        Pillar 8: Passive backend interceptor for UI Notification Badges.
        Calculates low stock alerts globally for admin.
        """
        if session.get('role') == 'ADMIN':
            from app.models.product_model import Product
            # Using 10 as the threshold
            low_stock_count = Product.query.filter(Product.stock <= 10).count()
            return {'global_low_stock_count': low_stock_count}
        return {'global_low_stock_count': 0}

    @flask_app.context_processor
    def inject_sidebar_data():
        """
        Amazon-style sidebar with real 7-day logic:
        - Best Sellers: most sold qty in last 7 days
        - New Releases: products added in last 7 days
        - Trending: most frequently ordered in last 7 days
        - Categories: only those with active products
        """
        if session.get('role') != 'ADMIN':
            from app.models.product_model import Product
            from app.models.category_model import Category
            from app.models.sales_order_item_model import SalesOrderItem
            from app.models.sales_order_model import SalesOrder
            from app.models.enums import CommonStatus, ProductStatus
            from app.extensions import db
            from sqlalchemy import func
            from datetime import datetime, timedelta

            try:
                seven_days_ago = datetime.utcnow() - timedelta(days=7)

                # Best Sellers: highest total quantity sold in last 7 days
                top_sold = db.session.query(
                    SalesOrderItem.pro_id,
                    func.sum(SalesOrderItem.quantity).label('total_qty')
                ).join(
                    SalesOrder, SalesOrder.order_id == SalesOrderItem.order_id
                ).filter(
                    SalesOrder.order_date >= seven_days_ago
                ).group_by(SalesOrderItem.pro_id)\
                .order_by(func.sum(SalesOrderItem.quantity).desc())\
                .limit(4).all()

                best_sellers = []
                if top_sold:
                    ids = [r.pro_id for r in top_sold]
                    best_sellers = Product.query.filter(
                        Product.pro_id.in_(ids),
                        Product.status == ProductStatus.ACTIVE
                    ).all()
                    order_map = {pid: i for i, pid in enumerate(ids)}
                    best_sellers.sort(key=lambda p: order_map.get(p.pro_id, 999))

                # New Releases: created within last 7 days
                new_releases = Product.query.filter(
                    Product.status == ProductStatus.ACTIVE,
                    Product.created_at >= seven_days_ago
                ).order_by(Product.created_at.desc()).limit(4).all()

                # Trending: most distinct orders in last 7 days
                trend_rows = db.session.query(
                    SalesOrderItem.pro_id,
                    func.count(SalesOrderItem.order_id.distinct()).label('cnt')
                ).join(
                    SalesOrder, SalesOrder.order_id == SalesOrderItem.order_id
                ).filter(
                    SalesOrder.order_date >= seven_days_ago
                ).group_by(SalesOrderItem.pro_id)\
                .order_by(func.count(SalesOrderItem.order_id.distinct()).desc())\
                .limit(4).all()

                trending = []
                if trend_rows:
                    ids = [r.pro_id for r in trend_rows]
                    trending = Product.query.filter(
                        Product.pro_id.in_(ids),
                        Product.status == ProductStatus.ACTIVE
                    ).all()
                    order_map = {pid: i for i, pid in enumerate(ids)}
                    trending.sort(key=lambda p: order_map.get(p.pro_id, 999))

                # Categories with at least one active product
                active_cat_ids = [r[0] for r in db.session.query(Product.cat_id).filter(
                    Product.status == ProductStatus.ACTIVE
                ).distinct().all()]

                cats_with_products = []
                if active_cat_ids:
                    cats_with_products = Category.query.filter(
                        Category.status == CommonStatus.ACTIVE,
                        Category.cat_id.in_(active_cat_ids)
                    ).all()

                return {
                    'sidebar_best_sellers': best_sellers,
                    'sidebar_new_releases': new_releases,
                    'sidebar_trending': trending,
                    'sidebar_categories': cats_with_products
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
        return {
            'sidebar_best_sellers': [],
            'sidebar_new_releases': [],
            'sidebar_trending': [],
            'sidebar_categories': []
        }