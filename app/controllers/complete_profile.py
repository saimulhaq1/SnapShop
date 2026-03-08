from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import (Customer, Category, Cart, Address, Country, ZipCode, 
                        CommonStatus, Product)
from app.extensions import db
from sqlalchemy.orm import joinedload
from decimal import Decimal
import re
from datetime import datetime

shop_bp = Blueprint('complete_profile', __name__)

@shop_bp.route('/categories')
def view_categories():
    """View all product categories."""
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)



@shop_bp.route('/complete-profile')
def complete_profile():
    user_id = session.get('user_id')
    if not user_id: 
        return redirect(url_for('login.login'))
    
    user = Customer.query.get(user_id)
    countries = Country.query.all()
    db_items = Cart.query.filter_by(customer_id=user_id).all()
    grand_total = sum(float(item.total) for item in db_items) if db_items else 0.0
    
    return render_template('complete_profile.html', user=user, countries=countries, 
                           cart_items=db_items, grand_total=grand_total)

@shop_bp.route('/save-profile', methods=['POST'])
def save_profile():
    user_id = session.get('user_id')
    user = Customer.query.get(user_id)
    if not user: 
        return redirect(url_for('login.login'))
        
    user.mobile_no = request.form.get('mobile')
    zip_input = request.form.get('zip_code')
    zip_rec = ZipCode.query.filter_by(zip_code_name=zip_input).first()
    
    if not zip_rec:
        zip_rec = ZipCode(zip_code_name=zip_input, city_id=1, status=CommonStatus.ACTIVE)
        db.session.add(zip_rec)
        db.session.flush()

    street_val = request.form.get('address')
    if user.addresses:
        user.addresses[0].address = street_val
        user.addresses[0].zip_code_id = zip_rec.zip_code_id
    else:
        new_addr = Address(address=street_val, zip_code_id=zip_rec.zip_code_id, customer_id=user.customer_id)
        db.session.add(new_addr)

    try:
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for('cart.checkout'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('complete_profile.complete_profile'))