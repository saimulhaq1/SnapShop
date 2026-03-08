from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, abort
from app.models import SalesOrder, SalesOrderItem, Customer, Address, ZipCode, City, OrderStatus, Product, Payment, PaymentStatus, PaymentMethod, db
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime
from app.middleware import admin_permission_required
from app.models.notification_model import Notification
from app.extensions import socketio

# Blueprint naming matches your base.html expectations
order_bp = Blueprint('order', __name__)

# --- 1. ORDER LIST VIEW (Restored & Optimized for UI) ---
@order_bp.route('/order')
def order_list():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))

    user_id = session.get('user_id')
    role = session.get('role')
    is_admin = role == 'ADMIN'
    print(f"DEBUG: Order History - User ID: {user_id}, Role: {role}")

    q = request.args.get('q', '').strip()
    search_type = request.args.get('search_type', '')
    status_val = request.args.get('status', '')
    direction = request.args.get('direction', 'desc')

    # Base query
    query = SalesOrder.query.options(joinedload(SalesOrder.customer_link))

    if not is_admin:
        query = query.filter(SalesOrder.customer_id == user_id)

    # Search Filters
    if q:
        try:
            if search_type == 'order_id':
                query = query.filter(SalesOrder.order_id == int(q))
            elif search_type == 'customer' and is_admin:
                query = query.join(Customer, SalesOrder.customer_id == Customer.customer_id) \
                             .filter(Customer.name.ilike(f"%{q}%"))
            elif search_type == 'date':
                query = query.filter(SalesOrder.order_date.cast(db.String).ilike(f"%{q}%"))
            elif not search_type and not is_admin:
                # Customer general search (ID or placeholder)
                if q.isdigit():
                    query = query.filter(SalesOrder.order_id == int(q))
                else:
                    query = query.outerjoin(SalesOrderItem).outerjoin(Product).filter(Product.name.ilike(f"%{q}%"))
        except ValueError:
            flash("Numeric search required for Order ID.", "warning")

    if status_val in OrderStatus.__members__:
        query = query.filter(SalesOrder.status == OrderStatus[status_val])

    # Sorting
    if direction == 'asc':
        query = query.order_by(SalesOrder.order_id.asc())
    else:
        query = query.order_by(SalesOrder.order_id.desc())

    orders_data = query.all()

    # Pre-formatting to Dictionary to prevent Jinja "Lazy Loading" crashes
    clean_orders = []
    for o in orders_data:
        clean_orders.append({
            'id': o.order_id,
            'total': float(o.total_amount or 0),
            'status': o.status.name if o.status else 'PENDING',
            'date': o.order_date.strftime("%d %b, %Y") if o.order_date else "N/A",
            'customer_name': o.customer_link.name if (is_admin and o.customer_link) else "N/A"
        })
    
    print(f"DEBUG: Orders sent to UI: {len(clean_orders)}")
    return render_template('order.html', order=clean_orders, OrderStatus=OrderStatus, is_admin=is_admin)

# --- 2. FINAL CHECKOUT LOGIC (Restored old Calculation & Payment logic) ---
# Checkout logic moved to cart_controller.py

# --- 3. STATUS UPDATES ---
@order_bp.route('/update-status/<int:id>', methods=['POST'])
@admin_permission_required('hide_order_page', 'Update Order Status')
def update_order_status(id):
    # Eager load payments and methods to avoid N+1 and potential detach errors
    order = SalesOrder.query.options(
        joinedload(SalesOrder.payments).joinedload(Payment.method)
    ).get_or_404(id)
    
    new_status = request.form.get('status')
    
    if new_status in OrderStatus.__members__:
        # 1. Update Order Status
        order.status = OrderStatus[new_status]
        
        # 2. Update Payment Logic (Conditional Triggers)
        for payment in order.payments:
            if not payment.method:
                continue
                
            method_name = payment.method.pay_method_name
            
            # Logic: Cards/Wallets are paid upon PROCESSING or SHIPPED status
            if method_name in ['Card', 'Digital Wallet'] and new_status in ['PROCESSING', 'SHIPPED', 'DELIVERED']:
                payment.status = PaymentStatus.PAID
                
            # Logic: COD is paid only upon DELIVERED, otherwise UNPAID
            elif method_name == 'Cash on Delivery':
                if new_status == 'DELIVERED':
                    payment.status = PaymentStatus.PAID
                else:
                    # Revert to UNPAID if status changes back
                    payment.status = PaymentStatus.UNPAID

        # --- REVENUE TRACKING LOGIC ---
        if order.status == OrderStatus.CANCELLED:
            if order.is_revenue_tracked:
                order.customer_link.total_spent = float(order.customer_link.total_spent or 0) - float(order.total_amount)
                order.total_paid = 0.00
                order.is_revenue_tracked = False
        else:
            # If any payment attached to this order is PAID, we track the revenue
            is_paid = any(p.status == PaymentStatus.PAID for p in order.payments)
            if is_paid and not order.is_revenue_tracked:
                order.customer_link.total_spent = float(order.customer_link.total_spent or 0) + float(order.total_amount)
                order.total_paid = float(order.total_amount)
                order.is_revenue_tracked = True
            elif not is_paid and order.is_revenue_tracked:
                order.customer_link.total_spent = float(order.customer_link.total_spent or 0) - float(order.total_amount)
                order.total_paid = 0.00
                order.is_revenue_tracked = False

        db.session.commit() 
        
        # Notify Customer of Status Update
        notif = Notification(
            user_id=order.customer_id,
            recipient_role='CUSTOMER',
            type='ORDER_STATUS',
            title=f'SnapShop Order {new_status.title()}',
            message=f'Your order #{order.order_id} is now {new_status.title()}.',
            link=url_for('order.order_list')
        )
        db.session.add(notif)
        db.session.commit()
        
        socketio.emit('customer_alert', {
            'type': 'ORDER_STATUS',
            'title': notif.title,
            'message': notif.message,
            'link': notif.link
        }, room=f'user_{order.customer_id}')
        
        flash(f"Order #{id} status updated to {new_status.title()}. Payment status synchronized.", "success")
        
    return redirect(url_for('order.order_list'))

@order_bp.route('/order/<int:id>')
def order_detail(id):
    is_admin = session.get('role') == 'ADMIN'
    o = SalesOrder.query.options(
        joinedload(SalesOrder.customer_link), 
        joinedload(SalesOrder.payments).joinedload(Payment.method),
        joinedload(SalesOrder.order_items).joinedload(SalesOrderItem.product)
    ).get_or_404(id)
    
    if not is_admin and o.customer_id != session.get('user_id'): 
        abort(403)
        
    return render_template('order_detail.html', o=o, OrderStatus=OrderStatus, is_admin=is_admin)