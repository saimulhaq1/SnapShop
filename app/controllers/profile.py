from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
from app.models import Customer
from app.extensions import db
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import hashlib
import os

profile_bp = Blueprint('profile', __name__)

def get_gravatar_url(email):
    """Generates a Gravatar URL from an email address."""
    if not email:
        return "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
    
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"

@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile_settings():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('login.login'))
        
    user = Customer.query.get(user_id)
    
    if request.method == 'POST':
        # --- Handle Image Upload ---
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                try:
                    filename = secure_filename(f"user_{user.customer_id}_{file.filename}")
                    # Ensure directory exists
                    upload_folder = os.path.join(current_app.root_path, 'static/assets/img/avatars')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file.save(os.path.join(upload_folder, filename))
                    user.profile_pic = filename
                    flash("Profile picture updated!", "success")
                except Exception as e:
                    flash(f"Error saving image: {str(e)}", "warning")
        # ---------------------------

        if request.form.get('name'):
             user.name = request.form.get('name')
             
        if request.form.get('mobile'):
             user.mobile_no = request.form.get('mobile')
        
        # Remove Bank Name update as field is removed from UI
        # user.bank_name = request.form.get('bank_name') 
        # user.bank_account_no = request.form.get('bank_no')
        
        new_pass = request.form.get('password')
        confirm_pass = request.form.get('confirm_password')

        if new_pass:
            if new_pass != confirm_pass:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('profile.profile_settings'))
            
            user.password = generate_password_hash(new_pass)
            flash("Password updated successfully!", "success")
            
        try:
            db.session.commit()
            if not new_pass: # Avoid double flash if password updated
                flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Update failed: {str(e)}", "danger")
            
        return redirect(url_for('profile.profile_settings'))
    
    # --- Avatar Logic ---
    avatar_url = ""
    if user.profile_pic and user.profile_pic != 'default_user.png':
        # Use locally uploaded image
        avatar_url = url_for('static', filename=f'assets/img/avatars/{user.profile_pic}')
    else:
        # Use Gravatar
        avatar_url = get_gravatar_url(user.email)
    # --------------------
        
    return render_template('profile.html', user=user, avatar_url=avatar_url)