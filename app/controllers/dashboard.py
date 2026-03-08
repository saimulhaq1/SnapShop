from flask import Blueprint, render_template, session, redirect, url_for, request
from sqlalchemy import func
from app import db
from app.models import (
    Customer, Product, SalesOrder, SalesOrderItem, Payment, 
    PaymentStatus, ProductStatus, OrderStatus
)
# Import the security decorator
from app.middleware import admin_permission_required
from app.extensions import socketio
from app.models.notification_model import Notification

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
# Global Page Lock: If 'hide_dashboard' is ON, show the locking card
@admin_permission_required('hide_dashboard', 'Dashboard Analytics')
def dashboard():
    """
    Dashboard Controller: 
    Exclusively for Admins. Calculates analytics while respecting 
    Super Admin and Staff permissions.
    """
    role = session.get('role')
    
    # 1. PRIMARY ROLE LOCK
    # If not an admin, redirect to product catalog (normal customer flow)
    if role not in ['ADMIN', 'STAFF']:
        return redirect(url_for('product.products'))

    # Load granular permissions dictionary from the session
    perms = session.get('session_user_permissions', {})

    # 2. GRANULAR WIDGET LOGIC
    # These counts only calculate if the specific widget isn't hidden by the Super Admin
    
    # Customer Count (Dash Widget)
    total_customers = 0
    if not perms.get('dash_customers'):
        total_customers = Customer.query.filter_by(role='customer').count()
    
    # Product Count (Dash Widget)
    total_products = 0
    if not perms.get('dash_products'):
        total_products = Product.query.count()
    
    # Total Orders (Dash Widget)
    total_orders = 0
    if not perms.get('dash_orders'):
        total_orders = SalesOrder.query.count()
        
    # Low Stock / Inventory Health
    low_stock_count = 0
    if not perms.get('dash_inventory'):
        low_stock_count = Product.query.filter(Product.stock < 10).count()

    # 3. REVENUE & PROFIT LOGIC
    total_revenue = 0
    total_net_profit = 0
    
    # Revenue Card
    if not perms.get('dash_revenue'):
        total_revenue = db.session.query(
            func.sum(Payment.paid_amount)
        ).filter(
            Payment.status == PaymentStatus.PAID
        ).scalar() or 0

    # Profit Card
    if not perms.get('dash_profit'):
        all_products = Product.query.all()
        for product in all_products:
            sale_price = float(product.sale_price or 0)
            buy_price = float(product.buy_price or 0)
            stock_count = product.stock or 0
            total_net_profit += (sale_price - buy_price) * stock_count

    # 4. RECENT ACTIVITY TABLE
    recent_orders = []
    if not perms.get('dash_recent_orders'):
        recent_orders = SalesOrder.query.order_by(
            SalesOrder.order_date.desc()
        ).limit(5).all()

    # 5. CHART.JS & QUICK-ACTION UI METRICS
    from datetime import datetime, timedelta
    from sqlalchemy import cast, Date, desc
    
    # Pending Shipments (PENDING or PROCESSING)
    pending_shipments = SalesOrder.query.filter(
        SalesOrder.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING])
    ).count()
    
    # Top 5 Selling Products Data
    top_products_query = db.session.query(
        Product.name,
        func.sum(SalesOrderItem.quantity).label('total_sold')
    ).join(SalesOrderItem).group_by(Product.pro_id).order_by(desc('total_sold')).limit(5).all()
    
    top_products_labels = [p[0] for p in top_products_query]
    top_products_data = [int(p[1]) for p in top_products_query]
    
    # Revenue over the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    revenue_query = db.session.query(
        cast(Payment.payment_date, Date).label('day'),
        func.sum(Payment.paid_amount).label('total')
    ).filter(
        Payment.status == PaymentStatus.PAID,
        Payment.payment_date >= seven_days_ago
    ).group_by('day').order_by('day').all()
    
    revenue_labels = [r[0].strftime('%b %d') for r in revenue_query]
    revenue_data = [float(r[1]) for r in revenue_query]

    return render_template(
        'dashboard.html',
        total_customers=total_customers,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_profit_with_gst=total_net_profit, 
        recent_orders=recent_orders,
        low_stock_count=low_stock_count,
        pending_shipments=pending_shipments,
        top_products_labels=top_products_labels,
        top_products_data=top_products_data,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data,
        is_admin=True,
        perms=perms # Pass perms to template for UI-level card hiding
    )

@dashboard_bp.route('/dashboard/broadcast_sale', methods=['POST'])
@admin_permission_required('hide_dashboard', 'Broadcast Sale')
def broadcast_sale():
    """Admin function to broadcast an alert to users or other admins."""
    # Grab custom message and target from modal
    custom_title = request.form.get('broadcast_title', 'Flash Sale!').strip()
    custom_message = request.form.get('broadcast_message', 'Check out the catalog now!').strip()
    target_role = request.form.get('broadcast_target', 'CUSTOMER')
    notif_type = 'SALE' if target_role == 'CUSTOMER' else 'SYSTEM'
    
    notifs_to_insert = []
    
    if target_role == 'CUSTOMER':
        targets = Customer.query.filter_by(role='CUSTOMER').all()
    else:
        targets = Customer.query.filter(Customer.role.in_(['ADMIN', 'STAFF'])).all()
        
    for user in targets:
        notifs_to_insert.append(Notification(
            user_id=user.customer_id,
            recipient_role=target_role,
            type=notif_type,
            title=custom_title if custom_title else 'Flash Sale is LIVE!',
            message=custom_message if custom_message else 'A massive new sale just went live. Check out the catalog now!',
            link=url_for('product.products') if target_role == 'CUSTOMER' else url_for('dashboard.dashboard')
        ))
        
    db.session.add_all(notifs_to_insert)
    db.session.commit()
    
    # Payload for socket
    payload = {
        'type': notif_type,
        'title': custom_title if custom_title else 'Flash Sale is LIVE!',
        'message': custom_message if custom_message else 'A massive new sale just went live.',
        'link': url_for('product.products') if target_role == 'CUSTOMER' else url_for('dashboard.dashboard')
    }
    
    if target_role == 'CUSTOMER':
        socketio.emit('customer_alert', payload, room='customer_room')
    else:
        socketio.emit('admin_alert', payload, room='admin_room')
        
    from flask import flash
    flash(f"Global Broadcast sent to all {target_role.capitalize()}s!", 'success')
    return redirect(url_for('dashboard.dashboard'))