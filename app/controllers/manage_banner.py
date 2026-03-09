import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from app.models import Banner
from app import db
from app.middleware import admin_permission_required

banner_bp = Blueprint('banner_admin', __name__)

UPLOAD_FOLDER = 'app/static/assets/img/banners'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@banner_bp.route('/admin/banners')
@admin_permission_required('hide_banner_page', 'Manage Banners')
def manage_banners():
    if session.get('role') != 'ADMIN':
        return redirect(url_for('login.login'))
    
    banners = Banner.query.order_by(Banner.sort_order.asc(), Banner.created_at.desc()).all()
    # Assume base.html needs perms check for menu highlights
    perms = session.get('session_user_permissions', {}) 
    return render_template('manage_banners.html', banners=banners, perms=perms)

@banner_bp.route('/admin/banners/add', methods=['POST'])
@admin_permission_required('hide_banner_page', 'Add Banner')
def add_banner():
    if request.method == 'POST':
        title = request.form.get('title')
        sort_order = request.form.get('sort_order', 0)
        
        if 'image' not in request.files:
            flash("No file part", "danger")
            return redirect(url_for('banner_admin.manage_banners'))
            
        file = request.files['image']
        
        if file.filename == '':
            flash("No selected file", "warning")
            return redirect(url_for('banner_admin.manage_banners'))
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Ensure folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            file.save(upload_path)
            
            try:
                sort_val = int(sort_order)
            except ValueError:
                sort_val = 0
                
            new_banner = Banner(title=title, image_url=filename, sort_order=sort_val)
            db.session.add(new_banner)
            db.session.commit()
            
            flash(f"Banner '{title}' successfully added.", "success")
        else:
            flash("Invalid file type. Allowed: jpg, png, gif, webp.", "danger")
            
    return redirect(url_for('banner_admin.manage_banners'))

@banner_bp.route('/admin/banners/delete/<int:id>', methods=['GET', 'POST'])
@admin_permission_required('hide_banner_page', 'Delete Banner')
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    title = banner.title or "Banner"
    
    # Optionally delete file from storage to save space
    if banner.image_url:
        file_path = os.path.join(UPLOAD_FOLDER, banner.image_url)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass 
                
    db.session.delete(banner)
    db.session.commit()
    flash(f"Banner '{title}' deleted successfully.", "info")
    return redirect(url_for('banner_admin.manage_banners'))
