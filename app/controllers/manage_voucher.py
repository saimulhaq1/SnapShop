from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from app.models import Voucher, Category, db
from app.middleware import admin_permission_required
from datetime import datetime

voucher_admin_bp = Blueprint('voucher_admin', __name__)

@voucher_admin_bp.route('/admin/vouchers')
@admin_permission_required('hide_voucher_page', 'Manage Vouchers')
def list_vouchers():
    if session.get('role') != 'ADMIN':
        abort(403)
    
    # Eager load category to avoid N+1 queries
    vouchers = Voucher.query.order_by(Voucher.created_at.desc()).all()
    return render_template('manage_vouchers.html', vouchers=vouchers)

@voucher_admin_bp.route('/admin/vouchers/add', methods=['GET', 'POST'])
@admin_permission_required('hide_voucher_page', 'Add Voucher')
def add_voucher():
    if session.get('role') != 'ADMIN':
        abort(403)
        
    categories = Category.query.all()
    
    if request.method == 'POST':
        code = request.form.get('code').strip().upper()
        name = request.form.get('name').strip()
        discount_type = request.form.get('discount_type')
        discount_value = request.form.get('discount_value')
        category_id = request.form.get('category_id') # empty string if all categories
        min_cart_value = request.form.get('min_cart_value') or 0
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        new_customer_only = request.form.get('new_customer_only') == 'on'
        first_order_only = request.form.get('first_order_only') == 'on'
        one_time_use = request.form.get('one_time_use') == 'on'
        
        # Validation
        if not code or not name or not discount_value or not start_date_str or not end_date_str:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for('voucher_admin.add_voucher'))
            
        # Check uniqueness
        if Voucher.query.filter_by(code=code).first():
            flash(f"Voucher code '{code}' already exists.", "danger")
            return redirect(url_for('voucher_admin.add_voucher'))
            
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            
            if start_date >= end_date:
                flash("End date must be after start date.", "danger")
                return redirect(url_for('voucher_admin.add_voucher'))
                
            new_voucher = Voucher(
                code=code,
                name=name,
                discount_type=discount_type,
                discount_value=float(discount_value),
                category_id=int(category_id) if category_id else None,
                min_cart_value=float(min_cart_value),
                start_date=start_date,
                end_date=end_date,
                new_customer_only=new_customer_only,
                first_order_only=first_order_only,
                one_time_use=one_time_use
            )
            
            db.session.add(new_voucher)
            db.session.commit()
            flash(f"Voucher '{code}' added successfully!", "success")
            return redirect(url_for('voucher_admin.list_vouchers'))
        except ValueError as e:
            flash(f"Invalid input data: {str(e)}", "danger")
            return redirect(url_for('voucher_admin.add_voucher'))
            
    return render_template('add_voucher.html', categories=categories)

@voucher_admin_bp.route('/admin/vouchers/edit/<int:id>', methods=['GET', 'POST'])
@admin_permission_required('hide_voucher_page', 'Edit Voucher')
def edit_voucher(id):
    if session.get('role') != 'ADMIN':
        abort(403)
        
    voucher = Voucher.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        code = request.form.get('code').strip().upper()
        name = request.form.get('name').strip()
        discount_type = request.form.get('discount_type')
        discount_value = request.form.get('discount_value')
        category_id = request.form.get('category_id') # empty string if all categories
        min_cart_value = request.form.get('min_cart_value') or 0
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        new_customer_only = request.form.get('new_customer_only') == 'on'
        first_order_only = request.form.get('first_order_only') == 'on'
        one_time_use = request.form.get('one_time_use') == 'on'
        
        # Validation
        if not code or not name or not discount_value or not start_date_str or not end_date_str:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for('voucher_admin.edit_voucher', id=id))
            
        # Check uniqueness, ignoring current voucher
        existing = Voucher.query.filter_by(code=code).first()
        if existing and existing.voucher_id != id:
            flash(f"Voucher code '{code}' already exists for another voucher.", "danger")
            return redirect(url_for('voucher_admin.edit_voucher', id=id))
            
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            
            if start_date >= end_date:
                flash("End date must be after start date.", "danger")
                return redirect(url_for('voucher_admin.edit_voucher', id=id))
                
            voucher.code = code
            voucher.name = name
            voucher.discount_type = discount_type
            voucher.discount_value = float(discount_value)
            voucher.category_id = int(category_id) if category_id else None
            voucher.min_cart_value = float(min_cart_value)
            voucher.start_date = start_date
            voucher.end_date = end_date
            voucher.new_customer_only = new_customer_only
            voucher.first_order_only = first_order_only
            voucher.one_time_use = one_time_use
            
            db.session.commit()
            flash(f"Voucher '{code}' updated successfully!", "success")
            return redirect(url_for('voucher_admin.list_vouchers'))
        except ValueError as e:
            flash(f"Invalid input data: {str(e)}", "danger")
            return redirect(url_for('voucher_admin.edit_voucher', id=id))
            
    return render_template('edit_voucher.html', voucher=voucher, categories=categories)

@voucher_admin_bp.route('/admin/vouchers/delete/<int:id>', methods=['POST'])
@admin_permission_required('hide_voucher_page', 'Delete Voucher')
def delete_voucher(id):
    if session.get('role') != 'ADMIN':
        abort(403)
        
    voucher = Voucher.query.get_or_404(id)
    # Check if voucher is used
    if voucher.usage_count > 0 or voucher.usages:
        flash(f"Cannot delete voucher '{voucher.code}' because it has already been used.", "danger")
        return redirect(url_for('voucher_admin.list_vouchers'))
        
    db.session.delete(voucher)
    db.session.commit()
    flash(f"Voucher '{voucher.code}' deleted successfully.", "info")
    return redirect(url_for('voucher_admin.list_vouchers'))
