from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
import json
from app import db
from app.models import Customer
from werkzeug.security import generate_password_hash
from app.middleware import admin_permission_required

staff_bp = Blueprint('admin_staff', __name__)

# --- AJAX PERMISSIONS FETCH ---
@staff_bp.route('/staff/get-permissions/<int:admin_id>')
def get_admin_perms(admin_id):
    admin = Customer.query.get_or_404(admin_id)
    # Using the model helper to return a dict
    return jsonify(admin.get_permissions() if hasattr(admin, 'get_permissions') else json.loads(admin.permissions or '{}'))

# --- CREATE ADMIN ACCOUNT ---
@staff_bp.route('/staff/create-employee', methods=['GET', 'POST'])
@admin_permission_required('manage_roles', 'Staff Creation')
def create_employee():
    user = Customer.query.get(session.get('user_id'))
    # Security: Only Super Admin (no 'created_by') can access
    if session.get('role') != 'ADMIN' or (user and user.created_by is not None):
        flash("Unauthorized: Only the Super Admin can manage staff accounts.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        name, email = request.form.get('name'), request.form.get('email')
        password, confirm = request.form.get('password'), request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('admin_staff.create_employee'))

        if Customer.query.filter_by(email=email).first():
            flash("Email already exists!", "warning")
            return redirect(url_for('admin_staff.create_employee'))

        new_emp = Customer(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role='admin',
            permissions='{}', 
            created_by=session.get('user_id')
        )
        
        db.session.add(new_emp)
        db.session.commit()
        flash(f"Admin account for {name} created!", "success")
        return redirect(url_for('admin_staff.manage_roles'))

    return render_template('admin/create_admin.html')

# --- MANAGE ROLES & DUTIES ---
@staff_bp.route('/staff/manage-roles', methods=['GET', 'POST'])
@admin_permission_required('manage_roles', 'Role Assignment')
def manage_roles():
    # Only Super Admin access check
    user = Customer.query.get(session.get('user_id'))
    if session.get('role') != 'ADMIN' or (user and user.created_by is not None):
        flash("Unauthorized: Only the Super Admin can assign roles.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    admins = Customer.query.filter(Customer.role == 'ADMIN', Customer.customer_id != session.get('user_id')).all()

    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        if not admin_id:
            flash("No admin selected.", "warning")
            return redirect(url_for('admin_staff.manage_roles'))

        # 1. Collect all checked permissions from the form dynamically
        # Filters out admin_id so only the toggle switches remain
        permissions_dict = {key: True for key in request.form.keys() if key != 'admin_id'}
        
        # 2. Update the Database
        target_user = Customer.query.get(admin_id)
        if target_user:
            target_user.permissions = json.dumps(permissions_dict)
            db.session.commit()
            
            # 3. SESSION SYNC: If the admin is editing THEIR OWN roles, update session immediately
            if int(admin_id) == session.get('user_id'):
                session['session_user_permissions'] = permissions_dict
                session.modified = True

            flash(f"Permissions updated successfully for {target_user.name}", "success")
        
        return redirect(url_for('admin_staff.manage_roles'))

    return render_template('admin/manage_roles.html', admins=admins)

# --- DELETE ADMIN ---
@staff_bp.route('/staff/delete-employee/<int:id>', methods=['POST'])
@admin_permission_required('manage_roles', 'Staff Deletion')
def delete_employee(id):
    user = Customer.query.get(session.get('user_id'))
    if session.get('role') != 'ADMIN' or (user and user.created_by is not None):
        abort(403)

    target_user = Customer.query.get_or_404(id)
    try:
        db.session.delete(target_user)
        db.session.commit()
        flash(f"Account for {target_user.name} removed.", "success")
    except:
        db.session.rollback()
        flash("User cannot be deleted due to active history.", "danger")

    return redirect(url_for('admin_staff.manage_roles'))