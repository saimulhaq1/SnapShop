from flask import Blueprint, render_template, request, session, flash
from app.models import Product, Category, Brand, ProductStatus, Banner
from sqlalchemy.orm import joinedload
from app.middleware import admin_permission_required
from app.extensions import db

catalog_bp = Blueprint('product', __name__)

@catalog_bp.route('/')
@catalog_bp.route('/product')
@admin_permission_required('hide_product_page', 'Product Catalog')
def products():
    """Main listing with Recursive Category Filtering (Parent + Sub-categories)."""
    is_admin = session.get('role') == 'ADMIN'
    perms = session.get('session_user_permissions', {})
    
    selected_cat_id = request.args.get('category_id', type=int)
    selected_brand_id = request.args.get('brand_id', type=int)
    q = request.args.get('q', '').strip()
    direction = request.args.get('direction', 'desc')
    
    category_name = "All Products"

    query = Product.query.options(
        joinedload(Product.category).joinedload(Category.parent_node), 
        joinedload(Product.tax_rule),
        joinedload(Product.brand)
    )

    # Recursive Category Logic
    if selected_cat_id:
        cat_obj = Category.query.get(selected_cat_id)
        if cat_obj:
            category_name = cat_obj.cat_name
            sub_categories = Category.query.filter_by(parent_cat_id=selected_cat_id).all()
            all_relevant_ids = [selected_cat_id] + [sub.cat_id for sub in sub_categories]
            query = query.filter(Product.cat_id.in_(all_relevant_ids))

    # Brand Filter
    if selected_brand_id:
        query = query.filter(Product.brand_id == selected_brand_id)
        # Optionally update category_name or add a breadcrumb context for brand
        brand_obj = Brand.query.get(selected_brand_id)
        if brand_obj:
            category_name = f"Brand: {brand_obj.brand_name}"

    # Search Filters
    # --- ADVANCED SEARCH FILTERING ---
    search_by = request.args.get('search_by', 'name')
    operator = request.args.get('operator', '=')
    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status_filter', '')
    
    # Base Query construction already happened above with joined loads
    
    if q:
        if search_by == 'name':
            query = query.filter(Product.name.ilike(f'%{q}%'))
        elif search_by == 'code':
             query = query.filter(Product.product_code.ilike(f'%{q}%'))
        elif search_by == 'barcode':
             if is_admin: query = query.filter(Product.barcode.ilike(f'%{q}%'))
        elif search_by == 'category':
            query = query.join(Category).filter(Category.cat_name.ilike(f'%{q}%'))
        elif search_by.startswith('cat_'):
            try:
                cat_id = int(search_by.split('_')[1])
                query = query.filter(Product.cat_id == cat_id)
            except (IndexError, ValueError):
                pass
            if q:
                query = query.filter(Product.name.ilike(f'%{q}%'))
        elif search_by == 'brand':
            query = query.join(Brand).filter(Brand.brand_name.ilike(f'%{q}%'))
        elif search_by == 'price' or (is_admin and search_by == 'stock'):
            try:
                val = float(q)
                column = Product.sale_price if search_by == 'price' else Product.stock
                
                if operator == '>':
                    query = query.filter(column > val)
                elif operator == '<':
                    query = query.filter(column < val)
                else:
                    query = query.filter(column == val)
            except ValueError:
                flash("Invalid number for search", "warning")

    # Status Filtering
    if is_admin:
        if status_filter:
            query = query.filter(Product.status == ProductStatus[status_filter])
    else:
        # Customers see ACTIVE and OUT_OF_STOCK, but OUT_OF_STOCK items are forced to the bottom
        query = query.filter(Product.status.in_([ProductStatus.ACTIVE, ProductStatus.OUT_OF_STOCK]))

    sort_col = Product.sale_price
    
    # Sort out of stock to the bottom for customers natively via DB
    if not is_admin:
        from sqlalchemy import case
        stock_order = case(
            (Product.status == ProductStatus.OUT_OF_STOCK, 1),
            else_=0
        )
        if direction == 'asc':
            query = query.order_by(stock_order.asc(), sort_col.asc())
        else:
            query = query.order_by(stock_order.asc(), sort_col.desc())
    else:
        query = query.order_by(sort_col.asc() if direction == 'asc' else sort_col.desc())

    # --- Pillar 2: Fetch Banners & Categories for UI ---
    banners = []
    parent_categories = []
    trending_products = []
    top_sold_products = []
    
    # Fetch Categories that have at least one product
    cat_query = Category.query.join(Product, Category.cat_id == Product.cat_id).distinct()
    
    if not is_admin:
        banners = Banner.query.order_by(Banner.sort_order.asc()).all()
        # Active and OUT OF STOCK categories to match product filter
        parent_categories = cat_query.filter(Product.status.in_([ProductStatus.ACTIVE, ProductStatus.OUT_OF_STOCK])).all()
        
        # --- Pillar 4: Amazon Sidebar Queries ---
        # 1. Trending Products (Most recently added)
        trending_products = Product.query.filter_by(status=ProductStatus.ACTIVE).order_by(Product.created_at.desc()).limit(5).all()
        
        # 2. Top Sold Products (Most ordered quantity from SalesOrderItem)
        from sqlalchemy import func
        from app.models.sales_order_item_model import SalesOrderItem
        
        top_sold_products = db.session.query(Product).join(SalesOrderItem).group_by(Product.pro_id).order_by(func.sum(SalesOrderItem.quantity).desc()).filter(Product.status == ProductStatus.ACTIVE).limit(5).all()
        
    else:
        parent_categories = cat_query.all()

    return render_template('product.html', products=query.all(), ProductStatus=ProductStatus,
                           is_admin=is_admin, perms=perms, current_category_name=category_name,
                           banners=banners, parent_categories=parent_categories,
                           trending_products=trending_products, top_sold_products=top_sold_products)

@catalog_bp.route('/product/<int:id>', endpoint='product_detail')
def product_detail(id):
    from app.models import ProductReview, VoteTracking
    from sqlalchemy.orm import subqueryload

    product = Product.query.options(
        joinedload(Product.category).joinedload(Category.parent_node),
        joinedload(Product.tax_rule)
    ).get_or_404(id)

    # Fetch top-level reviews with replies + votes eagerly loaded
    reviews = (
        ProductReview.query
        .filter_by(product_id=id, parent_id=None)
        .options(
            subqueryload(ProductReview.votes),
            subqueryload(ProductReview.replies).subqueryload(ProductReview.votes)
        )
        .order_by(ProductReview.created_at.desc())
        .all()
    )

    # Compute aggregate rating from top-level reviews with ratings
    rated_reviews = [r for r in reviews if r.rating is not None]
    avg_rating = round(sum(r.rating for r in rated_reviews) / len(rated_reviews), 1) if rated_reviews else None
    review_count = len(rated_reviews)
    
    # Star distribution: {5: count, 4: count, ...}
    star_distribution = {i: sum(1 for r in rated_reviews if r.rating == i) for i in range(5, 0, -1)}

    # Map: review_id -> user vote type
    user_id = session.get("user_id")
    user_votes = {}
    if user_id:
        all_ids = [r.review_id for r in reviews]
        for r in reviews:
            all_ids += [rep.review_id for rep in r.replies]
        if all_ids:
            votes = VoteTracking.query.filter(
                VoteTracking.review_id.in_(all_ids),
                VoteTracking.customer_id == user_id
            ).all()
            user_votes = {v.review_id: v.vote_type for v in votes}

    # Pillar 6: Smart Recommendations
    recommendations = Product.query.filter_by(cat_id=product.cat_id, status=ProductStatus.ACTIVE).filter(Product.pro_id != product.pro_id).order_by(Product.created_at.desc()).limit(4).all()

    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count,
        star_distribution=star_distribution,
        user_votes=user_votes,
        recommendations=recommendations
    )

@catalog_bp.route('/api/search', endpoint='api_search')
def api_search():
    from flask import request, jsonify
    
    q = request.args.get('q', '').strip()
    cat_id = request.args.get('cat_id', '')
    
    if not q:
        return jsonify([])
        
    query = Product.query.filter(Product.status.in_([ProductStatus.ACTIVE, ProductStatus.OUT_OF_STOCK]))
    
    if cat_id and cat_id.isdigit():
        query = query.filter_by(cat_id=int(cat_id))
        
    # Search by product name or code
    query = query.filter(db.or_(
        Product.name.ilike(f'%{q}%'),
        Product.product_code.ilike(f'%{q}%')
    )).limit(8).all()
    
    results = []
    for p in query:
        results.append({
            'id': p.pro_id,
            'name': p.name,
            'price': "{:,.2f}".format(p.sale_price),
            'image_url': url_for('static', filename='assets/img/products/' + (p.image_url or 'default_product.png')),
            'url': url_for('product.product_detail', id=p.pro_id),
            'category': p.category.cat_name if p.category else 'N/A'
        })
        
    return jsonify(results)

@catalog_bp.route('/api/product/<int:id>', endpoint='api_product_detail')
def api_product_detail(id):
    from flask import jsonify
    product = Product.query.get_or_404(id)
    
    # Calculate prices matching template logic
    sale_val = float(product.sale_price) if product.sale_price else 0.0
    p_disc = float(product.discount) if product.discount else 0.0
    c_disc = float(product.category.discount) if product.category and product.category.discount else 0.0
    total_disc_percent = p_disc + c_disc
    
    discounted_sale = sale_val * (1.0 - (total_disc_percent / 100.0))
    tax_rate = float(product.tax_rule.rate) if product.tax_rule else 0.0
    tax_val = discounted_sale * (tax_rate / 100.0)
    final_price = discounted_sale + tax_val
    
    return jsonify({
        'id': product.pro_id,
        'name': product.name,
        'code': product.product_code or 'N/A',
        'description': product.description or 'No description available.',
        'image_url': url_for('static', filename='assets/img/products/' + (product.image_url or 'default_product.png')),
        'original_price': "{:,.2f}".format(sale_val),
        'final_price': "{:,.2f}".format(final_price),
        'has_discount': total_disc_percent > 0,
        'discount_percent': total_disc_percent,
        'stock': product.stock,
        'is_out_of_stock': product.stock <= 0 or product.status.name == 'OUT_OF_STOCK',
        'url': url_for('product.product_detail', id=product.pro_id),
        'add_to_cart_url': url_for('cart.add_to_cart', product_id=product.pro_id)
    })

@catalog_bp.route('/product/<int:id>/review', methods=['POST'])
def submit_review(id):
    import os
    import uuid
    from werkzeug.utils import secure_filename
    from flask import request, redirect, flash, session, url_for, current_app
    from app.models import ProductReview, ReviewPhoto
    
    if 'user_id' not in session:
        flash("Please log in to submit a review.", "warning")
        return redirect(url_for('login.login'))

    product = Product.query.get_or_404(id)
    user_id = session.get('user_id')
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    if not comment:
        flash("Review comment cannot be empty.", "danger")
        return redirect(url_for('product.product_detail', id=id) + '#reviews')
        
    if not rating or not (1 <= rating <= 5):
        flash("Please provide a valid rating between 1 and 5.", "danger")
        return redirect(url_for('product.product_detail', id=id) + '#reviews')
        
    # Check if user already reviewed this product
    existing_review = ProductReview.query.filter_by(product_id=id, customer_id=user_id, parent_id=None).first()
    if existing_review:
        flash("You have already reviewed this product.", "info")
        return redirect(url_for('product.product_detail', id=id) + '#reviews')
        
    # Check if this is a verified purchase
    is_verified = ProductReview.check_if_verified(user_id, id)
    
    new_review = ProductReview(
        product_id=id,
        customer_id=user_id,
        rating=rating,
        comment=comment,
        verified_purchase=is_verified
    )
    
    # Process Photos
    photos = request.files.getlist('photos')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    photo_count = 0
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'reviews')
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in photos:
        if file and file.filename:
            if photo_count >= 3:
                break
            
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if ext in ALLOWED_EXTENSIONS:
                unique_filename = f"{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                new_photo = ReviewPhoto(photo_url=f"uploads/reviews/{unique_filename}")
                new_review.photos.append(new_photo)
                photo_count += 1
    
    try:
        db.session.add(new_review)
        db.session.commit()
        if is_verified:
            flash("Thank you for your verified review!", "success")
        else:
            flash("Your review has been submitted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while submitting your review.", "danger")
        
    return redirect(url_for('product.product_detail', id=id) + '#reviews')
