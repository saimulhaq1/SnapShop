from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app import db
from app.models import Category, CommonStatus

category_registry_bp = Blueprint('categories', __name__)

@category_registry_bp.route('/categories')
def category_list():
    """Dual Purpose Route: Admin Registry and Customer Storefront."""
    is_admin = session.get('role') == 'ADMIN'
    perms = session.get('session_user_permissions', {})
    
    if is_admin and perms.get('hide_category_page'):
        flash("Access Denied: You do not have permission to view Category Management.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    q = request.args.get('q', '').strip()
    search_type = request.args.get('search_type', '')
    status_filter = request.args.get('status', '')
    direction = request.args.get('direction', 'asc')

    # Eager load parent_node to avoid N+1 queries in the template
    query = Category.query.options(db.joinedload(Category.parent_node))

    # Search logic
    if q:
        try:
            if search_type == 'name':
                query = query.filter(Category.cat_name.ilike(f'%{q}%'))
            elif search_type == 'id':
                query = query.filter(Category.cat_id == int(q))
            elif search_type == 'parent':
                ParentCategory = db.aliased(Category)
                query = query.join(ParentCategory, Category.parent_cat_id == ParentCategory.cat_id) \
                             .filter(ParentCategory.cat_name.ilike(f'%{q}%'))
        except ValueError:
            flash("Please enter a valid numeric ID.", "warning")

    if status_filter in CommonStatus.__members__:
        query = query.filter(Category.status == CommonStatus[status_filter])

    # Sorting
    sort_logic = Category.cat_id.asc() if direction == 'asc' else Category.cat_id.desc()
    
    return render_template('categories.html', 
                            categories=query.order_by(sort_logic).all(), 
                            all_statuses=CommonStatus, 
                            CommonStatus=CommonStatus,
                            is_admin=is_admin,
                            session_user_permissions=perms)