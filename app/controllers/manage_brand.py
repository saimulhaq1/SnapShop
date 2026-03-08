from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.models import Brand, db
from app.middleware import admin_permission_required

brand_bp = Blueprint('manage_brand', __name__)

@brand_bp.route('/brand/manage', methods=['GET'])
@admin_permission_required('hide_product_page', 'Brand Management')
def manage_brands():
    brands = Brand.query.order_by(Brand.brand_name).all()
    return render_template('manage_brand.html', brands=brands)

@brand_bp.route('/brand/add', methods=['POST'])
@admin_permission_required('prod_add', 'Add Brand')
def add_brand():
    brand_name = request.form.get('brand_name', '').strip()
    
    if not brand_name:
        flash("Brand name is required.", "danger")
        return redirect(url_for('manage_brand.manage_brands'))
    
    existing = Brand.query.filter_by(brand_name=brand_name).first()
    if existing:
        flash(f"Brand '{brand_name}' already exists.", "warning")
        return redirect(url_for('manage_brand.manage_brands'))
    
    try:
        new_brand = Brand(brand_name=brand_name)
        db.session.add(new_brand)
        db.session.commit()
        flash(f"Brand '{brand_name}' created successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating brand: {str(e)}", "danger")
        
    return redirect(url_for('manage_brand.manage_brands'))

@brand_bp.route('/brand/edit/<int:id>', methods=['POST'])
@admin_permission_required('prod_action', 'Edit Brand')
def edit_brand(id):
    brand = Brand.query.get_or_404(id)
    new_name = request.form.get('brand_name', '').strip()
    
    if not new_name:
        flash("Brand name cannot be empty.", "danger")
        return redirect(url_for('manage_brand.manage_brands'))
        
    try:
        brand.brand_name = new_name
        db.session.commit()
        flash("Brand updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating brand: {str(e)}", "danger")
        
    return redirect(url_for('manage_brand.manage_brands'))

@brand_bp.route('/brand/delete/<int:id>', methods=['POST'])
@admin_permission_required('prod_action', 'Delete Brand')
def delete_brand(id):
    brand = Brand.query.get_or_404(id)
    
    if brand.products:
        flash(f"Cannot delete brand '{brand.brand_name}' because it has linked products.", "danger")
        return redirect(url_for('manage_brand.manage_brands'))
        
    try:
        db.session.delete(brand)
        db.session.commit()
        flash("Brand deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting brand: {str(e)}", "danger")
        
    return redirect(url_for('manage_brand.manage_brands'))
