import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.customer_model import Customer
from app.models import Cart
from app.models.enums import CommonStatus
from app.extensions import db
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    email = ""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # 1. SIMULATED TESTING LOGIC
        if email == "admin@test.com":
            session.clear()
            session.update({'user_id': 999, 'role': 'ADMIN', 'username': 'Admin Tester', 'is_super_admin': True, 'session_user_permissions': {}})
            flash("Logged in as Tester (ADMIN)", "info")
            return redirect(url_for('dashboard.dashboard'))

        # 2. REAL DATABASE LOGIC
        user = Customer.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Block unverified accounts
            if user.status == CommonStatus.INACTIVE:
                flash(
                    "Your account is not yet verified. Please check your email inbox for the activation link. "
                    f'<a href="{url_for("register_forget.resend_verification", email=email)}" class="alert-link">Resend verification email</a>',
                    "warning"
                )
                return redirect(url_for('login.login'))

            session.clear()
            session['user_id'] = user.customer_id
            session['username'] = user.name
            session['role'] = user.role.value if hasattr(user.role, 'value') else user.role

            # --- PERSISTENT CART MERGE LOGIC ---
            # 1. Get Guest Cart from Session
            guest_cart = session.get('cart', {})
            
            # 2. Get User's Saved Cart from DB
            saved_items = Cart.query.filter_by(customer_id=user.customer_id).all()
            saved_cart_map = {item.product_id: item for item in saved_items}
            
            # 3. Merge Guest Items into DB
            if guest_cart:
                from app.models import Product # ensure Product is available
                for pid_str, qty in guest_cart.items():
                    pid = int(pid_str)
                    if pid in saved_cart_map:
                        # Item exists in DB -> Update Qty
                        saved_cart_map[pid].qty += qty
                        # Update Total (Price * New Qty)
                        product = Product.query.get(pid)
                        if product:
                             from decimal import Decimal
                             saved_cart_map[pid].total = float(Decimal(str(product.sale_price)) * Decimal(str(saved_cart_map[pid].qty)))
                    else:
                        # Item new to DB -> Create Record
                        product = Product.query.get(pid)
                        if product:
                            from decimal import Decimal
                            total_price = float(Decimal(str(product.sale_price)) * Decimal(str(qty)))
                            new_item = Cart(
                                customer_id=user.customer_id,
                                product_id=pid,
                                qty=qty,
                                total=total_price
                            )
                            db.session.add(new_item)
                
                db.session.commit()
            
            # 4. Re-hydrate Session from Updated DB
            # This ensures the session reflects the final merged state (DB + Guest)
            final_db_items = Cart.query.filter_by(customer_id=user.customer_id).all()
            final_cart_session = {}
            for item in final_db_items:
                final_cart_session[str(item.product_id)] = item.qty
            
            session['cart'] = final_cart_session
            session.modified = True
            # -----------------------------------

            # Load Permissions
            perms = {}
            if getattr(user.role, 'value', user.role) == 'ADMIN' and user.permissions:
                try:
                    perms = json.loads(user.permissions)
                    if isinstance(perms, str): perms = json.loads(perms)
                except Exception: perms = {}
            
            session['session_user_permissions'] = perms
            session['is_super_admin'] = (getattr(user.role, 'value', user.role) == 'ADMIN' and user.created_by is None)

            flash(f"Welcome back, {user.name}!", "success")
            
            # SMART REDIRECT
            if getattr(user.role, 'value', user.role) in ['ADMIN', 'STAFF']:
                if not perms.get('hide_dashboard'): return redirect(url_for('dashboard.dashboard'))
                elif not perms.get('hide_customer_page'): return redirect(url_for('customer.customers'))
                elif not perms.get('hide_product_page'): return redirect(url_for('product.products'))
                return redirect(url_for('customer.profile_settings'))
            
            return redirect(url_for('product.products'))
        
        flash("Invalid email or password.", "danger")

    return render_template('login.html', email=email)

@login_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    # Using '.login' tells Flask to look inside the SAME blueprint
    # This solves the BuildError: 'auth_session.login' vs 'login.login'
    return redirect(url_for('.login'))