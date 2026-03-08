from flask import Blueprint, redirect, url_for, flash
from app import db
from app.models import Country, TaxRate, CommonStatus

system_bp = Blueprint('system', __name__)

@system_bp.route('/admin/setup-database')
def setup_database():
    try:
        # Sync Country
        pk = Country.query.filter_by(country_code="PK").first()
        if not pk:
            pk = Country(country_name="Pakistan", country_code="PK", status=CommonStatus.ACTIVE)
            db.session.add(pk)
            db.session.flush()

        # Clean old Tax Rates
        TaxRate.query.filter(TaxRate.country_id == pk.country_id, TaxRate.tax_name != 'GST').delete()

        # Seed GST Rates
        rates = [0, 5, 10, 16]
        for r in rates:
            if not TaxRate.query.filter_by(country_id=pk.country_id, tax_name="GST", rate=r).first():
                db.session.add(TaxRate(country_id=pk.country_id, tax_name="GST", rate=r, status=CommonStatus.ACTIVE))

        db.session.commit()
        flash("Database synced successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"System Error: {str(e)}", "danger")

    return redirect(url_for('product.products'))

# --- Professional Pages ---

@system_bp.route('/about')
def about():
    return render_template('about.html')

@system_bp.route('/support')
def support():
    return render_template('support.html')

# --- Notification APIs ---

from flask import request, jsonify, session, render_template
from app.models.notification_model import Notification

@system_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    user_id = session.get('user_id')
    role = session.get('role', 'CUSTOMER')
    
    if not user_id and role != 'ADMIN':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        if role == 'ADMIN':
            # Mark all admin notifications as read (only global ones or explicit user ones)
            from sqlalchemy import or_
            unread = Notification.query.filter(
                Notification.recipient_role == 'ADMIN',
                Notification.is_read == False,
                or_(Notification.user_id.is_(None), Notification.user_id == user_id)
            ).all()
        else:
            # Mark all user notifications as read
            unread = Notification.query.filter_by(user_id=user_id, is_read=False).all()
            
        for notif in unread:
            notif.is_read = True
            
        db.session.commit()
        return jsonify({'success': True, 'marked': len(unread)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@system_bp.route('/notifications/<int:notif_id>/delete', methods=['POST'])
def delete_notification(notif_id):
    user_id = session.get('user_id')
    role = session.get('role', 'CUSTOMER')
    
    if not user_id and role != 'ADMIN':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        notif = Notification.query.get_or_404(notif_id)
        
        # Verify ownership or admin
        if role != 'ADMIN' and notif.user_id != user_id:
            # If it's a legacy global broadcast, fake success so it clears from the customer UI
            if notif.user_id is None and notif.recipient_role == 'CUSTOMER':
                return jsonify({'success': True})
            return jsonify({'success': False, 'message': 'Forbidden'}), 403
            
        # Only delete if it's not a legacy global broadcast for an admin OR if it's explicitly owned.
        # Admins deleting a global notification will delete it for all admins, this is existing intended legacy behavior.
        if role == 'ADMIN' and notif.user_id is None and notif.recipient_role == 'ADMIN':
            db.session.delete(notif)
        else:
            db.session.delete(notif)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500