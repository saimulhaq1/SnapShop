from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from app.models import (Product, Customer, Address, ZipCode, SalesOrder, 
                        SalesOrderItem, Payment, PaymentMethod, OrderStatus, 
                        PaymentStatus, Cart, Voucher, VoucherUsage, Notification, db)
from app.extensions import socketio
                        
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime

# Initialize the blueprint
cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart/update_qty', methods=['POST'])
def update_qty():
    """AJAX endpoint to update quantity and sync with Database."""
    data = request.get_json()
    product_id = data.get('product_id')
    new_qty = int(data.get('qty'))
    user_id = session.get('user_id')

    # 1. Update Session
    cart = session.get('cart', {})
    cart[str(product_id)] = new_qty
    session['cart'] = cart
    session.modified = True
    
    # 2. Update Database if user is logged in
    if user_id:
        db_item = Cart.query.filter_by(customer_id=user_id, product_id=product_id).first()
        if db_item:
            db_item.qty = new_qty
            product = Product.query.get(product_id)
            if product:
                db_item.total = float(Decimal(str(product.sale_price)) * Decimal(str(new_qty)))
            db.session.commit()

    return jsonify({"success": True})

@cart_bp.route('/cart/apply_voucher', methods=['POST'])
def apply_voucher():
    code = request.form.get('voucher_code', '').strip().upper()
    user_id = session.get('user_id')
    
    if not user_id:
        flash("Please log in to apply a voucher.", "warning")
        return redirect(url_for('cart.cart_view'))
        
    # 1. Does the code exist?
    voucher = Voucher.query.filter_by(code=code).first()
    
    if not voucher:
        flash("Invalid voucher code.", "danger")
        return redirect(url_for('cart.cart_view'))
        
    # 2. Is it active and not expired? (Using local datetime)
    now = datetime.now()
    print(f"DEBUG Voucher Validating: Current Time={now}, Start={voucher.start_date}, End={voucher.end_date}")
    
    if now < voucher.start_date or now > voucher.end_date:
        flash("This voucher is expired or not yet active.", "danger")
        return redirect(url_for('cart.cart_view'))
        
    # Category Check & Min Cart Value Check
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart.cart_view'))
        
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.pro_id.in_(product_ids)).all()
    product_map = {p.pro_id: p for p in products}
    
    subtotal = Decimal('0.00')
    has_valid_item = False
    
    for pid, qty in cart.items():
        p = product_map.get(int(pid))
        if p:
            line_total = Decimal(str(p.sale_price)) * Decimal(str(qty))
            subtotal += line_total
            if not voucher.category_id or p.category_id == voucher.category_id:
                has_valid_item = True
                
    if voucher.category_id and not has_valid_item:
        if voucher.category:
            flash(f"This voucher is only valid for {voucher.category.cat_name} products.", "danger")
        else:
            flash("This voucher is not valid for any items in your cart.", "danger")
        return redirect(url_for('cart.cart_view'))
        
    # 3. Does cart meet minimum amount?
    if voucher.min_cart_value and subtotal < Decimal(str(voucher.min_cart_value)):
        flash(f"Cart total must be at least RS {voucher.min_cart_value} to use this voucher.", "danger")
        return redirect(url_for('cart.cart_view'))

    # 4. Is the user eligible?
    user = Customer.query.get(user_id)
    if voucher.new_customer_only:
        time_diff = now - user.join_date
        if time_diff.total_seconds() > 86400: # older than 24 hours
            flash("This voucher is only for new customers.", "danger")
            return redirect(url_for('cart.cart_view'))
            
    if voucher.first_order_only:
        successful_orders = SalesOrder.query.filter_by(customer_id=user_id, status=OrderStatus.DELIVERED).count()
        if successful_orders > 0:
            flash("This voucher is only for your first order.", "danger")
            return redirect(url_for('cart.cart_view'))
            
    # 5. Has user used it before? (One-time use)
    if voucher.one_time_use:
        usage = VoucherUsage.query.filter_by(voucher_id=voucher.voucher_id, customer_id=user_id).first()
        if usage:
            flash("You have already used this voucher.", "danger")
            return redirect(url_for('cart.cart_view'))
            
    session['applied_voucher'] = voucher.code
    flash(f"Success! Voucher '{voucher.code}' Applied!", "success")
    return redirect(url_for('cart.cart_view'))

@cart_bp.route('/cart/remove_voucher', methods=['POST'])
def remove_voucher():
    if 'applied_voucher' in session:
        session.pop('applied_voucher')
        flash("Voucher removed.", "info")
    return redirect(url_for('cart.cart_view'))

@cart_bp.route('/cart')
def cart_view():
    """View the current shopping shopping cart."""
    cart = session.get('cart', {})
    cart_items = []
    delivery_charge = Decimal('0.00')
    
    # Optimize query to fetch products with relationships in one go
    if cart:
        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.query.options(
            joinedload(Product.category),
            joinedload(Product.tax_rule)
        ).filter(Product.pro_id.in_(product_ids)).all()
        
        product_map = {p.pro_id: p for p in products}
        
        for pid, qty in cart.items():
            pid_int = int(pid)
            if pid_int in product_map:
                p = product_map[pid_int]
                cart_items.append({'product': p, 'qty': int(qty)})
                if not p.is_free_delivery:
                    item_delivery = Decimal(str(p.delivery_charge or 0))
                    if item_delivery > delivery_charge:
                        delivery_charge = item_delivery
            
    voucher_discount = Decimal('0.00')
    applied_voucher_code = session.get('applied_voucher')
    applied_voucher_obj = None
    if applied_voucher_code:
        v = Voucher.query.filter_by(code=applied_voucher_code).first()
        if v:
            # Re-verify conditions real quick just in case
            now = datetime.now()
            sub = Decimal('0.00') # raw subtotal
            valid_cat_sub = Decimal('0.00')
            has_valid_item = False
            for item in cart_items:
                p = item['product']
                q = Decimal(str(item['qty']))
                sp = Decimal(str(p.sale_price))
                line_total = sp * q
                sub += line_total
                if not v.category_id or p.category_id == v.category_id:
                    valid_cat_sub += line_total
                    has_valid_item = True
            
            if now >= v.start_date and now <= v.end_date and (not v.min_cart_value or sub >= Decimal(str(v.min_cart_value))) and has_valid_item:
                applied_voucher_obj = v
                if v.discount_type == 'Percentage':
                    voucher_discount = valid_cat_sub * (Decimal(str(v.discount_value)) / Decimal('100'))
                else:
                    voucher_discount = Decimal(str(v.discount_value))
                    if v.category_id and voucher_discount > valid_cat_sub:
                        voucher_discount = valid_cat_sub
                    elif not v.category_id and voucher_discount > sub:
                        voucher_discount = sub
            else:
                session.pop('applied_voucher', None)
                flash("Voucher condition no longer met. Removed.", "warning")

    return render_template('cart.html', cart_items=cart_items, delivery_charge=float(delivery_charge), 
                           voucher=applied_voucher_obj, voucher_discount=float(voucher_discount))

@cart_bp.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    """Adds a product to the session-based shopping cart."""
    if not session.get('user_id'):
        flash('Please login or create an account to begin shopping.', 'info')
        return redirect(url_for('login.login'))

    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product = Product.query.get_or_404(product_id)
    
    if product.stock <= 0:
        flash(f"Sorry, {product.name} is currently out of stock.", "danger")
        return redirect(url_for('product.products'))

    pid_str = str(product_id)
    if pid_str in cart:
        cart[pid_str] += 1
    else:
        cart[pid_str] = 1
        
    session['cart'] = cart
    session.modified = True
    
    # --- DB SYNC for Logged-In Users ---
    user_id = session.get('user_id')
    if user_id:
        db_item = Cart.query.filter_by(customer_id=user_id, product_id=product_id).first()
        if db_item:
            db_item.qty = cart[pid_str]
            db_item.total = float(Decimal(str(product.sale_price)) * Decimal(str(db_item.qty)))
        else:
            total_price = float(Decimal(str(product.sale_price)) * Decimal(str(cart[pid_str])))
            new_item = Cart(customer_id=user_id, product_id=product_id, qty=cart[pid_str], total=total_price)
            db.session.add(new_item)
        db.session.commit()
    # -----------------------------------
    
    flash(f"Added {product.name} to your cart!", "success")
    return redirect(request.referrer or url_for('product.products'))

@cart_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Updates the quantity of a specific item in the session cart."""
    cart = session.get('cart', {})
    try:
        new_qty = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        new_qty = 1

    pid_str = str(product_id)
    if pid_str in cart:
        if new_qty > 0:
            product = Product.query.get(product_id)
            if product and new_qty <= product.stock:
                cart[pid_str] = new_qty
                flash(f"Updated quantity for {product.name}.", "success")
                
                # --- DB SYNC ---
                user_id = session.get('user_id')
                if user_id:
                    db_item = Cart.query.filter_by(customer_id=user_id, product_id=product_id).first()
                    if db_item:
                        db_item.qty = new_qty
                        db_item.total = float(Decimal(str(product.sale_price)) * Decimal(str(new_qty)))
                        db.session.commit()
                # ---------------
            else:
                flash(f"Only {product.stock} units available for {product.name}.", "warning")
        else:
            cart.pop(pid_str)
            
            # --- DB SYNC (Remove) ---
            user_id = session.get('user_id')
            if user_id:
                Cart.query.filter_by(customer_id=user_id, product_id=product_id).delete()
                db.session.commit()
            # ------------------------
            
            flash("Item removed from cart.", "info")
            
        session['cart'] = cart
        session.modified = True
    
    return redirect(url_for('cart.cart_view'))

@cart_bp.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    """Directly removes an item from the cart."""
    cart = session.get('cart', {})
    pid_str = str(product_id)
    
    if pid_str in cart:
        cart.pop(pid_str)
        session['cart'] = cart
        session.modified = True
        
        # --- DB SYNC ---
        user_id = session.get('user_id')
        if user_id:
            Cart.query.filter_by(customer_id=user_id, product_id=product_id).delete()
            db.session.commit()
        # ---------------
        
        flash("Item removed from cart.", "info")
        
    return redirect(url_for('cart.cart_view'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Handle the order placement and payment logic."""
    user_id = session.get('user_id')
    if not user_id: 
        flash("Please Login or Create an Account to proceed.", "warning")
        return redirect(url_for('login.login'))

    user = Customer.query.get(user_id)
    cart_session = session.get('cart', {})
    
    if not cart_session:
        flash("Your cart is empty.", "info")
        return redirect(url_for('product.products'))

    address_rec = Address.query.filter_by(customer_id=user.customer_id).options(
        joinedload(Address.zip_code).joinedload(ZipCode.city)
    ).first()

    if not user.mobile_no or not address_rec:
        flash("Please complete your profile and address before checkout.", "warning")
        return redirect(url_for('complete_profile.complete_profile'))

    cart_details = []
    subtotal = Decimal('0.00')
    total_tax = Decimal('0.00')

    for pid, qty in cart_session.items():
        product = Product.query.options(
            joinedload(Product.tax_rule),
            joinedload(Product.category)
        ).get(int(pid))

        if not product:
            continue

        qty_dec = Decimal(str(qty))
        base_price = Decimal(str(product.sale_price or 0))
        p_disc = Decimal(str(product.discount or 0))
        c_disc = Decimal(str(product.category.discount if product.category else 0))
        total_disc = p_disc + c_disc

        discounted_price = base_price * (Decimal('1') - (total_disc / Decimal('100')))
        tax_rate = Decimal(str(product.tax_rule.rate if product.tax_rule else 0))
        tax_per_unit = discounted_price * (tax_rate / Decimal('100'))

        unit_price_incl_tax = discounted_price + tax_per_unit
        row_total = unit_price_incl_tax * qty_dec

        subtotal += discounted_price * qty_dec
        total_tax += tax_per_unit * qty_dec

        cart_details.append({
            'product': product,
            'qty': int(qty),
            'unit_price': float(unit_price_incl_tax),
            'row_total': float(row_total),
            'tax_rate': float(tax_rate)
        })

    # Compute delivery charge: max of all non-free items (0 if all free)
    delivery_charge = Decimal('0.00')
    for item in cart_details:
        p = item['product']
        if not p.is_free_delivery:
            item_dc = Decimal(str(p.delivery_charge or 0))
            if item_dc > delivery_charge:
                delivery_charge = item_dc

    voucher_discount = Decimal('0.00')
    applied_voucher_code = session.get('applied_voucher')
    applied_voucher_obj = None
    
    if applied_voucher_code:
        v = Voucher.query.filter_by(code=applied_voucher_code).first()
        if v:
            valid_cat_sub = Decimal('0.00')
            has_valid_item = False
            for item in cart_details:
                p = item['product']
                q = Decimal(str(item['qty']))
                # Use base sale price for voucher discount calculation
                sp = Decimal(str(p.sale_price))
                if not v.category_id or p.category_id == v.category_id:
                    valid_cat_sub += sp * q
                    has_valid_item = True
                    
            if has_valid_item:
                if v.discount_type == 'Percentage':
                    voucher_discount = valid_cat_sub * (Decimal(str(v.discount_value)) / Decimal('100'))
                else:
                    voucher_discount = Decimal(str(v.discount_value))
                    if v.category_id and voucher_discount > valid_cat_sub:
                        voucher_discount = valid_cat_sub
                    elif not v.category_id and voucher_discount > subtotal:
                        voucher_discount = subtotal
                applied_voucher_obj = v

    total_payable = subtotal + total_tax + delivery_charge - voucher_discount
    if total_payable < Decimal('0.00'):
        total_payable = Decimal('0.00')

    # ===============================
    # HANDLE ORDER SUBMISSION (POST)
    # ===============================
    if request.method == 'POST':
        print(f"DEBUG: Entering Checkout POST - User ID: {user_id}")
        try:
            # 1. Get Payment Info from Form
            pay_method_name = request.form.get('payment_method')
            print(f"DEBUG: Payment Method from Form: {pay_method_name}")
            
            # Map "Card" to "Card"
            # Map "Digital Wallet" to "Digital Wallet" (ID 4)
            # Map "COD" to "Cash on Delivery" (ID 1)
            
            db_name = pay_method_name
            if pay_method_name == 'COD':
                db_name = 'Cash on Delivery'
            elif pay_method_name == 'Digital Wallet':
                db_name = 'Digital Wallet'
                
            selected_method = PaymentMethod.query.filter_by(pay_method_name=db_name).first()
            
            if not selected_method:
                 # Fallback/Error Handling
                 if pay_method_name == 'Card':
                     selected_method = PaymentMethod.query.filter_by(pay_method_name='Card').first()
                 elif pay_method_name == 'Digital Wallet':
                      # Fallback if rename didn't work? Use ID 4
                      selected_method = PaymentMethod.query.get(4)
                 
            print(f"DEBUG: Selected Method: {selected_method.pay_method_name if selected_method else 'None'}")
            
            if not selected_method:
                flash("Invalid Payment Method Selected.", "danger")
                return redirect(url_for('cart.cart_view'))

            # 2. Create the Sales Order
            new_order = SalesOrder(
                customer_id=user.customer_id,
                address_id=address_rec.address_id,
                order_date=db.func.current_timestamp(),
                total_amount=total_payable,
                status=OrderStatus.PENDING 
            )
            db.session.add(new_order)
            db.session.flush() 

            # --- VOUCHER USAGE ---
            if applied_voucher_obj:
                usage = VoucherUsage(
                    voucher_id=applied_voucher_obj.voucher_id,
                    customer_id=user.customer_id,
                    order_id=new_order.order_id,
                    discount_applied=voucher_discount
                )
                applied_voucher_obj.usage_count += 1
                db.session.add(usage)
                session.pop('applied_voucher', None)

            # 3. Process Items
            for item in cart_details:
                product = item['product']
                qty = item['qty']

                if product.stock < qty:
                    db.session.rollback()
                    flash(f"Insufficient stock for {product.name}.", "danger")
                    return redirect(url_for('cart.cart_view'))

                qty_dec = Decimal(str(qty))
                tax_rate_dec = Decimal(str(item['tax_rate']))
                p_disc = Decimal(str(product.discount or 0))
                c_disc = Decimal(str(product.category.discount if product.category else 0))
                disc_base = Decimal(str(product.sale_price or 0)) * (Decimal('1') - ((p_disc + c_disc) / Decimal('100')))
                tax_amount = (disc_base * (tax_rate_dec / Decimal('100'))) * qty_dec

                order_item = SalesOrderItem(
                    order_id=new_order.order_id, 
                    pro_id=product.pro_id,
                    quantity=qty, 
                    unit_price=Decimal(str(item['unit_price'])),
                    tax_rate_at_purchase=tax_rate_dec, 
                    tax_amount=tax_amount
                )
                db.session.add(order_item)
                product.stock -= qty

            # 4. Create the Payment Record (Persistence Fix)
            # This ensures the selected method is saved, not just COD by default.
            new_payment = Payment(
                order_id=new_order.order_id, 
                method_id=selected_method.method_id if selected_method else 1,
                paid_amount=total_payable, 
                payment_date=db.func.current_timestamp(),
                status=PaymentStatus.UNPAID,
                # Store the wallet number or card number in the wallet_number field
                wallet_number=request.form.get('wallet_number') or request.form.get('card_number'),
                account_holder_name=request.form.get('account_holder_name') or request.form.get('name_on_card')
            )
            db.session.add(new_payment)

            db.session.commit()
            
            # 5. Clear Carts
            session.pop('cart', None) 
            Cart.query.filter_by(customer_id=user.customer_id).delete()
            
            # --- NOTIFICATIONS ---
            # To Admin
            admin_notif = Notification(
                recipient_role='ADMIN',
                type='ORDER',
                title=f'New SnapShop Order #{new_order.order_id}',
                message=f'{user.name} placed a new order for Rs. {total_payable}.',
                link=url_for('order.order_detail', id=new_order.order_id)
            )
            # To Customer
            cust_notif = Notification(
                user_id=user.customer_id,
                recipient_role='CUSTOMER',
                type='ORDER_STATUS',
                title='SnapShop Order Confirmed',
                message='Your order is made and is currently Pending.',
                link=url_for('order.order_list')
            )
            db.session.add_all([admin_notif, cust_notif])
            db.session.commit()
            
            # Fire real-time sockets
            socketio.emit('admin_alert', {
                'type': 'ORDER', 
                'title': admin_notif.title, 
                'message': admin_notif.message, 
                'link': admin_notif.link
            }, room='admin_room')
            
            socketio.emit('customer_alert', {
                'type': 'ORDER_STATUS', 
                'title': cust_notif.title, 
                'message': cust_notif.message, 
                'link': cust_notif.link
            }, room=f'user_{user.customer_id}')

            flash(f"Order placed successfully via {pay_method_name}!", "success")
            return redirect(url_for('order.order_list'))
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Checkout Failed: {str(e)}")
            flash(f"Error processing order: {str(e)}", "danger")

    return render_template(
        'checkout.html', 
        user=user, 
        cart_details=cart_details, 
        address_rec=address_rec,
        subtotal=float(subtotal), 
        total_tax=float(total_tax), 
        delivery_charge=float(delivery_charge),
        voucher_discount=float(voucher_discount),
        voucher=applied_voucher_obj,
        total_payable=float(total_payable)
    )