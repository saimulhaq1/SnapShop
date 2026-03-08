import os
import secrets
from flask import Blueprint, request, redirect, url_for, flash, session, abort, render_template
from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.utils import secure_filename
from app.models import Product, Category, Brand, TaxRate, ProductStatus, ProductImage, db
from app.middleware import admin_permission_required

inventory_bp = Blueprint('manage_product', __name__)

UPLOAD_FOLDER = 'app/static/assets/img/products'
GALLERY_FOLDER = 'app/static/assets/img/products/gallery'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{secrets.token_hex(8)}.{ext}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- MAIN MANAGEMENT ROUTE (ADD/EDIT) ---
@inventory_bp.route('/product/manage', defaults={'id': None}, methods=['GET', 'POST'])
@inventory_bp.route('/product/manage/<int:id>', methods=['GET', 'POST'])
@admin_permission_required('hide_product_page', 'Inventory Management')
def manage_product(id):
    if session.get('role') != 'ADMIN': abort(403) 
    perms = session.get('session_user_permissions', {})

    if (id is None and perms.get('prod_add')) or (id is not None and perms.get('prod_action')):
        flash("Unauthorized: Management access disabled.", "danger")
        return redirect(url_for('product.products'))

    product = Product.query.get_or_404(id) if id else Product()

    if request.method == 'POST':
        try:
            # --- 1. SERVER-SIDE VALIDATION & PREPARATION ---
            name = request.form.get('name', '').strip()
            cat_id = request.form.get('cat_id')
            # brand_id = request.form.get('brand_id') # Replaced by brand_name input
            buy_price_str = request.form.get('buy_price')
            sale_price_str = request.form.get('sale_price')
            stock_str = request.form.get('stock')
            code = request.form.get('product_code', '').strip()

            # Validation Checks
            if not name:
                flash("Please fill in the Product Name box", "danger")
                return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)
            
            if not code:
                 flash("Please fill in the Product Code (SKU) box", "danger")
                 return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)

            if not cat_id:
                flash("Please select a Category", "danger")
                return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)
            
            if not buy_price_str:
                flash("Please fill in the Buy Price box", "danger")
                return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)
            
            if not sale_price_str:
                flash("Please fill in the Sale Price box", "danger")
                return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)
            
            if not stock_str:
                flash("Please fill in the Stock Quantity box", "danger")
                return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)

            # --- 2. FILE UPLOAD LOGIC ---
            file = request.files.get('image_file')
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = generate_unique_filename(filename)
                if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                
                if product.image_url and product.image_url != 'default_product.png':
                    old_file_path = os.path.join(UPLOAD_FOLDER, product.image_url)
                    if os.path.exists(old_file_path):
                        try: os.remove(old_file_path)
                        except OSError: pass

                product.image_url = unique_filename
            elif not product.image_url:
                product.image_url = 'default_product.png'

            # --- 3. DATA MAPPING & TYPE CONVERSION ---
            try:
                product.name = name
                product.product_code = code
                product.article_no = request.form.get('article_no', '').strip()
                product.barcode = request.form.get('barcode', '').strip()
                product.description = request.form.get('description', '').strip()
                
                product.buy_price = float(buy_price_str)
                product.sale_price = float(sale_price_str)
                product.stock = int(stock_str)
                product.cat_id = int(cat_id)
                
                # --- BRAND: GET OR CREATE LOGIC ---
                brand_name_input = request.form.get('brand_name', '').strip()
                if brand_name_input:
                    # Check if brand exists (case-insensitive search could be better, but exact match for now)
                    existing_brand = Brand.query.filter_by(brand_name=brand_name_input).first()
                    if existing_brand:
                         product.brand_id = existing_brand.brand_id
                    else:
                        # Create new brand
                        new_brand = Brand(brand_name=brand_name_input)
                        db.session.add(new_brand)
                        db.session.flush() # Flush to get the new ID
                        product.brand_id = new_brand.brand_id
                        flash(f"New Brand '{brand_name_input}' created!", "info")
                else:
                    product.brand_id = None
                
                tax_id = request.form.get('tax_id')
                product.tax_id = int(tax_id) if tax_id else None
                
                product.discount = float(request.form.get('discount') or 0)
                
                # --- DELIVERY FIELDS ---
                product.is_free_delivery = request.form.get('is_free_delivery') == '1'
                if product.is_free_delivery:
                    product.delivery_charge = 0
                else:
                    product.delivery_charge = float(request.form.get('delivery_charge') or 0)
            except ValueError:
                flash("Invalid number format in Price or Stock fields.", "danger")
                return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)

            # --- 4. STATUS HANDLING ---
            status_name = request.form.get('status')
            if status_name in ProductStatus.__members__:
                product.status = ProductStatus[status_name]
                flag_modified(product, "status")
                
                # Force DB update via Raw SQL if editing an existing product
                if id:
                    db.session.execute(
                        text("UPDATE product SET status = :status WHERE pro_id = :id"),
                        {'status': status_name, 'id': id}
                    )

            # --- 5. SESSION COMMIT ---
            if id:
                db.session.merge(product)
            else:
                db.session.add(product)
            
            db.session.flush() 

            # --- 6. HANDLE DELETED EXISTING GALLERY IMAGES ---
            deleted_ids = request.form.get('deleted_existing_images', '')
            if deleted_ids:
                deleted_id_list = [int(i) for i in deleted_ids.split(',') if i.strip().isdigit()]
                if deleted_id_list:
                    images_to_delete = ProductImage.query.filter(
                        ProductImage.id.in_(deleted_id_list), 
                        ProductImage.product_id == product.pro_id
                    ).all()
                    for img in images_to_delete:
                        file_path = os.path.join(GALLERY_FOLDER, img.image_url)
                        if os.path.exists(file_path):
                            try: os.remove(file_path)
                            except OSError: pass
                        db.session.delete(img)

            # --- 7. HANDLE ADDITIONAL GALLERY IMAGES ---
            additional_images = request.files.getlist('additional_images')
            if additional_images:
                os.makedirs(GALLERY_FOLDER, exist_ok=True)
                for f in additional_images:
                    if f and f.filename != '' and allowed_file(f.filename):
                        safe_name = secure_filename(f.filename)
                        gallery_filename = generate_unique_filename(safe_name)
                        f.save(os.path.join(GALLERY_FOLDER, gallery_filename))
                        
                        new_img = ProductImage(product_id=product.pro_id, image_url=gallery_filename)
                        db.session.add(new_img)

            db.session.commit()
            
            flash(f"Success: Product {product.name} saved successfully.", "success")
            return redirect(url_for('product.products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            # Return form with data preserved (handled by template using request.form)
            return render_template('manage_product.html', product=product, categories=Category.query.all(), brands=Brand.query.all(), taxes=TaxRate.query.all(), ProductStatus=ProductStatus)

    return render_template('manage_product.html', 
                           product=product, 
                           categories=Category.query.all(), 
                           brands=Brand.query.all(),
                           taxes=TaxRate.query.all(), 
                           ProductStatus=ProductStatus)

# --- STANDALONE UPDATE ROUTE (Quick Updates) ---
@inventory_bp.route('/product/update/<int:product_id>', methods=['POST'])
@admin_permission_required('prod_action', 'Product Update')
def update_product(product_id):
    """Handles quick updates directly from the list view."""
    product = Product.query.get_or_404(product_id)
    
    try:
        new_status_str = request.form.get('status') 
        if new_status_str in ProductStatus.__members__:
            product.status = ProductStatus[new_status_str]
            flag_modified(product, "status")
            
            # Force Raw SQL for quick update
            db.session.execute(
                text("UPDATE product SET status = :status WHERE pro_id = :id"),
                {'status': new_status_str, 'id': product_id}
            )

        if request.form.get('discount'):
            product.discount = float(request.form.get('discount'))
        if request.form.get('sale_price'):
            product.sale_price = float(request.form.get('sale_price'))
        if request.form.get('stock'):
            product.stock = int(request.form.get('stock'))

        db.session.merge(product)
        db.session.commit()
        flash(f"Status for {product.name} updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Update failed: {str(e)}", "danger")

    return redirect(url_for('product.products'))

# --- DELETE ROUTE ---
@inventory_bp.route('/product/delete/<int:id>', methods=['POST'])
@admin_permission_required('hide_product_page', 'Product Deletion')
def delete_product(id):
    if session.get('session_user_permissions', {}).get('prod_action'):
        flash("Unauthorized: Deletion disabled.", "danger")
        return redirect(url_for('product.products'))

    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash("Product removed.", "success")
    except Exception:
        db.session.rollback()
        flash("Cannot delete: Linked to existing orders.", "danger")
    return redirect(url_for('product.products'))