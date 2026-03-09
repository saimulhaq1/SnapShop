from flask import Blueprint, request, jsonify, session, url_for
from datetime import datetime
from app import db
from app.models import Payment, PaymentStatus, Notification
from app.extensions import socketio
from app.middleware import admin_permission_required

payment_action_bp = Blueprint('payment_action', __name__)

@payment_action_bp.route('/payment/update_status/<int:id>', methods=['POST'])
@admin_permission_required('hide_payment_page', 'Payment Status Update')
def update_payment_status(id):
    """Admin only: Change payment status via AJAX."""
    if session.get('role') != 'ADMIN':
        return jsonify(success=False, message="Unauthorized"), 403

    payment = Payment.query.get_or_404(id)
    
    data = request.get_json() or {}
    status_name = data.get('status')

    if status_name in PaymentStatus.__members__:
        payment.status = PaymentStatus[status_name]
        
        # --- REVENUE TRACKING LOGIC ---
        order = payment.order
        if order and order.status != 'CANCELLED':  # Don't track if order is cancelled
            if payment.status == PaymentStatus.PAID and not order.is_revenue_tracked:
                order.customer_link.total_spent = float(order.customer_link.total_spent or 0) + float(order.total_amount)
                order.total_paid = float(order.total_amount)
                order.is_revenue_tracked = True
            elif payment.status != PaymentStatus.PAID and order.is_revenue_tracked:
                # E.g., Payment changed back to FAILED/UNPAID manually
                order.customer_link.total_spent = float(order.customer_link.total_spent or 0) - float(order.total_amount)
                order.total_paid = 0.00
                order.is_revenue_tracked = False

        if hasattr(payment, 'updated_at'):
            payment.updated_at = datetime.now()
            
        try:
            db.session.commit()
            
            # Notify Customer of Payment Status Update
            if order:
                notif = Notification(
                    user_id=order.customer_id,
                    recipient_role='CUSTOMER',
                    type='PAYMENT_STATUS',
                    title=f'SnapShop Payment {payment.status.name.title()}',
                    message=f'Payment for Order #{order.order_id} is now {payment.status.name}.',
                    link=url_for('payment.payments')
                )
                db.session.add(notif)
                db.session.commit()
                
                socketio.emit('customer_alert', {
                    'type': 'PAYMENT_STATUS',
                    'title': notif.title,
                    'message': notif.message,
                    'link': notif.link
                }, room=f'user_{order.customer_id}')
                
            return jsonify(success=True)
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message="Database update failed"), 500

    return jsonify(success=False, message="Invalid Status"), 400