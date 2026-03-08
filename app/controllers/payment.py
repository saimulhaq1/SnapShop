from flask import Blueprint, render_template, request, session, flash
from app import db
from app.models import Payment, PaymentMethod, PaymentStatus, SalesOrder
from app.middleware import admin_permission_required

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment')
@admin_permission_required('hide_payment_page', 'Financial Payment Ledger')
def payments():
    """Global Payment Ledger - View and Search functionality."""
    is_admin = session.get('role') == 'ADMIN'
    user_id = session.get('user_id')
    perms = session.get('session_user_permissions', {})

    q = request.args.get('q', '').strip()
    search_type = request.args.get('search_type', '')
    status_val = request.args.get('status', '')
    direction = request.args.get('direction', 'desc')

    # Base Query
    query = Payment.query.outerjoin(PaymentMethod)

    # Security: Customer isolation
    if not is_admin:
        query = query.join(SalesOrder).filter(SalesOrder.customer_id == user_id)

    # Search Filters
    if q:
        try:
            if search_type == 'id':
                query = query.filter(Payment.payment_id == int(q))
            elif search_type == 'order_id':
                query = query.filter(Payment.order_id == int(q))
            elif search_type == 'date':
                query = query.filter(Payment.payment_date.cast(db.String).ilike(f'%{q}%'))
            elif search_type == 'amount' and is_admin and not perms.get('pay_amount'): 
                query = query.filter(Payment.paid_amount == float(q))
            elif search_type == 'method':
                query = query.filter(PaymentMethod.pay_method_name.ilike(f"%{q}%"))
        except ValueError:
            flash("Numeric search required for ID or Amount.", "warning")

    if status_val in PaymentStatus.__members__:
        query = query.filter(Payment.status == PaymentStatus[status_val])

    sort_order = Payment.payment_id.asc() if direction == 'asc' else Payment.payment_id.desc()
    
    payments_data = query.order_by(sort_order).all()

    # Pre-formatting to Dictionary for Clean Data & Float Conversion
    clean_payments = []
    for p in payments_data:
        clean_payments.append({
            'payment_id': p.payment_id,
            'order_id': p.order_id,
            'method': p.method.pay_method_name if p.method else "Other",
            'date': p.payment_date.strftime("%d %b, %Y") if p.payment_date else "-",
            'amount': float(p.paid_amount or 0),
            'status': p.status.name if p.status else 'UNPAID',
            'holder': p.account_holder_name if p.account_holder_name else ("N/A" if p.method and p.method.pay_method_name == 'Cash on Delivery' else "-")
        })

    print(f"DEBUG: Payments sent to UI: {len(clean_payments)}")

    return render_template(
        'payment.html',
        payments=clean_payments,
        PaymentStatus=PaymentStatus,
        is_admin=is_admin,
        perms=perms
    )