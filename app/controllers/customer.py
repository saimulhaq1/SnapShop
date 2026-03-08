from flask import Blueprint, render_template, request, session, jsonify, abort
from app.models import Customer, CommonStatus, SalesOrder, Payment, Address, ZipCode, City
from app.extensions import db
from sqlalchemy.orm import joinedload
from app.middleware import admin_permission_required

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer')
@admin_permission_required('hide_customer_page', 'Customer Registry')
def customers():
    is_admin = session.get('role') == 'ADMIN'
    perms = session.get('session_user_permissions', {})
    
    q = request.args.get('q', '').strip()
    search_type = request.args.get('search_type', 'name')
    status_filter = request.args.get('status', '')
    direction = request.args.get('direction', 'asc') 

    query = Customer.query.filter(Customer.role == 'CUSTOMER').options(
        joinedload(Customer.addresses).joinedload(Address.zip_code).joinedload(ZipCode.city),
        joinedload(Customer.orders).joinedload(SalesOrder.payments).joinedload(Payment.method)
    )

    if q:
        if search_type == 'name':
            query = query.filter(Customer.name.ilike(f'%{q}%'))
        elif search_type == 'email' and not perms.get('cust_email'):
            query = query.filter(Customer.email.ilike(f'%{q}%'))
        elif search_type == 'mobile' and not perms.get('cust_mobile'):
            query = query.filter(Customer.mobile_no.ilike(f'%{q}%'))

    if status_filter in CommonStatus.__members__:
        query = query.filter(Customer.status == CommonStatus[status_filter])

    sort_col = Customer.customer_id
    query = query.order_by(sort_col.desc() if direction == 'desc' else sort_col.asc())
    
    all_shoppers = query.all()
    customer_data = []
    for c in all_shoppers:
        # Improved Address Logic
        city_name = "---"
        address_type = "---"
        
        if c.addresses:
            addr = c.addresses[0]
            address_type = addr.address_title or "General"
            if addr.zip_code and addr.zip_code.city:
                city_name = addr.zip_code.city.city_name
                
        payment_pref = "Not Set"
        if c.orders:
            sorted_orders = sorted(c.orders, key=lambda x: x.order_date, reverse=True)
            if sorted_orders and sorted_orders[0].payments:
                payment_pref = sorted_orders[0].payments[0].method.pay_method_name

        customer_data.append({
            'obj': c, 
            'city': city_name, 
            'address_type': address_type, 
            'payment_pref': payment_pref
        })

    return render_template('customer.html', customers=customer_data, CommonStatus=CommonStatus, 
                           is_admin=is_admin, session_user_permissions=perms)

@customer_bp.route('/customer/<int:customer_id>')
@admin_permission_required('hide_customer_page', 'Customer Profile View')
def customer_detail(customer_id):
    # Eager load orders and payments to calculate totals accurately (Clean Data Approach)
    customer = Customer.query.options(
        joinedload(Customer.orders).joinedload(SalesOrder.payments).joinedload(Payment.method),
        joinedload(Customer.addresses).joinedload(Address.zip_code)
    ).filter_by(customer_id=customer_id, role='CUSTOMER').first_or_404()

    # Calculate Total Paid directly from the DB field logic
    total_paid = 0.0
    
    if customer.orders:
        for order in customer.orders:
            # Read from DB correctly:
            order.paid_total = float(order.total_paid or 0)
            order.pending_total = float(order.total_amount or 0) - order.paid_total
            
            total_paid += order.paid_total

    print(f"DEBUG: Customer {customer_id} Total Paid: {total_paid}")

    return render_template('customer_detail.html', customer=customer, total_paid=total_paid, is_admin=True)

@customer_bp.route('/customer/update-status', methods=['POST'])
@admin_permission_required('hide_customer_page', 'Status Update')
def update_status():
    data = request.get_json()
    customer = Customer.query.get(data.get('customer_id'))
    if customer and data.get('status') in CommonStatus.__members__:
        try:
            customer.status = CommonStatus[data.get('status')]
            db.session.commit()
            return jsonify({"success": True})
        except:
            db.session.rollback()
            return jsonify({"success": False}), 500
    return jsonify({"success": False}), 400