from flask import Blueprint, render_template, request, session, jsonify
from sqlalchemy import asc, desc
from app import db  
from app.models import Address, Customer, ZipCode, City, CommonStatus
from app.middleware import admin_permission_required

# UPDATED: Using the name address_admin_bp to fix the ImportError
address_admin_bp = Blueprint('address', __name__)

@address_admin_bp.route('/addresses')
@admin_permission_required('hide_address_page', 'Global Address Registry')
def addresses():
    """Registry view for managing all system addresses."""
    is_admin = session.get('role') == 'ADMIN'

    # 1. Get parameters
    q = request.args.get('q', '').strip()
    search_type = request.args.get('search_type', '')
    status_filter = request.args.get('status', '')
    direction = request.args.get('direction', 'asc')

    # 2. Start Query
    query = Address.query

    # 3. Apply Admin Search Logic
    if q and search_type:
        if search_type == 'id':
            query = query.filter(Address.address_id == q)
        elif search_type == 'customer':
            query = query.join(Customer).filter(Customer.name.ilike(f'%{q}%'))
        elif search_type == 'title':
            query = query.filter(Address.address_title.ilike(f'%{q}%'))
        elif search_type == 'address':
            query = query.filter(Address.address.ilike(f'%{q}%'))
        elif search_type == 'city':
            query = query.join(ZipCode).join(City).filter(City.city_name.ilike(f'%{q}%'))
        elif search_type == 'zip':
            query = query.join(ZipCode).filter(ZipCode.zip_code_name.ilike(f'%{q}%'))

    # 4. Status Filter
    if status_filter in CommonStatus.__members__:
        query = query.filter(Address.status == CommonStatus[status_filter])

    # 5. Sorting Logic
    sort_logic = asc(Address.address_id) if direction == 'asc' else desc(Address.address_id)
    
    return render_template(
        'address.html', 
        addresses=query.order_by(sort_logic).all(), 
    )

@address_admin_bp.route('/address/update-status', methods=['POST'])
@admin_permission_required('hide_address_page', 'Update Address Status')
def update_address_status():
    """AJAX endpoint to update an address's status"""
    data = request.get_json()
    if not data or 'address_id' not in data or 'status' not in data:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
    address = Address.query.get(data['address_id'])
    if not address:
        return jsonify({'success': False, 'error': 'Address not found'}), 404
        
    try:
        new_status = CommonStatus[data['status'].upper()]
        address.status = new_status
        db.session.commit()
        return jsonify({'success': True})
    except KeyError:
        return jsonify({'success': False, 'error': 'Invalid status provided'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500