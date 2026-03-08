import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, redirect, url_for, flash, jsonify, session, render_template
from app import db
from app.models import Category, CommonStatus
from app.middleware import admin_permission_required

category_editor_bp = Blueprint('manage_category', __name__)

UPLOAD_FOLDER = 'app/static/assets/img/categories'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@category_editor_bp.route('/category/manage', methods=['GET', 'POST'])
@category_editor_bp.route('/category/manage/<int:id>', methods=['GET', 'POST'])
@admin_permission_required('hide_category_page', 'Category Editor')
def manage_category(id=None):
    perms = session.get('session_user_permissions', {})
    
    # Permission Checks
    if (id is None and perms.get('cat_add')) or (id is not None and perms.get('cat_action')):
        flash("Access Denied: Insufficient permissions for this action.", "danger")
        return redirect(url_for('categories.category_list'))

    category = Category.query.get_or_404(id) if id else Category()

    if request.method == 'POST':
        try:
            category.cat_name = request.form.get('cat_name')
            category.discount = float(request.form.get('discount') or 0)
            parent_id = int(request.form.get('parent_cat_id') or 0)
            category.parent_cat_id = parent_id if parent_id > 0 else None
            
            status_val = request.form.get('status')
            if status_val:
                category.status = CommonStatus[status_val]

            # Handle Image Upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_path = os.path.join(UPLOAD_FOLDER, filename)
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(upload_path)
                    
                    # Delete old image if updating
                    if id and category.image_url and category.image_url != 'default_category.png':
                        old_path = os.path.join(UPLOAD_FOLDER, category.image_url)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except OSError:
                                pass
                                
                    category.image_url = filename

            if not id: db.session.add(category)
            db.session.commit()
            flash(f"Category '{category.cat_name}' successfully saved!", "success")
            return redirect(url_for('categories.category_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"System Error: {str(e)}", "danger")

    return render_template('manage_category.html', 
                            category=category, 
                            all_categories=Category.query.all(), 
                            CommonStatus=CommonStatus)

@category_editor_bp.route('/category/delete/<int:cat_id>', methods=['POST'])
@admin_permission_required('hide_category_page', 'Category Deletion')
def delete_category(cat_id):
    if session.get('session_user_permissions', {}).get('cat_action'):
        return jsonify({"success": False, "message": "Access Denied"}), 403

    category = Category.query.get_or_404(cat_id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash("Category removed.", "success")
    except Exception:
        db.session.rollback()
        flash("Cannot delete: Linked to active products.", "danger")
    return redirect(url_for('categories.category_list'))

@category_editor_bp.route('/update-status/<int:id>/', methods=['POST'])
def update_status(id):
    if session.get('role') != 'ADMIN' or session.get('session_user_permissions', {}).get('cat_action'):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    category = Category.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in CommonStatus.__members__:
        category.status = CommonStatus[new_status]
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid status"}), 400