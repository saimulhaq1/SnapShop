from flask import Blueprint, request, jsonify
from app import db
from app.models import Address, CommonStatus
from app.middleware import admin_permission_required

# UPDATED: Using the name your __init__.py is looking for to fix the ImportError
address_api_bp = Blueprint('address_api', __name__)

@address_api_bp.route('/api/addresses/status', methods=['POST'])
@admin_permission_required('hide_address_page', 'Address Status Update')
def update_address_status():
    """API endpoint for updating address status via AJAX (JSON data)."""
    try:
        data = request.get_json()
        address_id = data.get('address_id')
        new_status = data.get('status')

        address = Address.query.get(address_id)
        if address and new_status in CommonStatus.__members__:
            address.status = CommonStatus[new_status]
            db.session.commit()
            return jsonify({"success": True, "message": "Status updated successfully"})
        
        return jsonify({"success": False, "message": "Invalid address or status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@address_api_bp.route('/address/update_status/<int:id>', methods=['POST'])
@admin_permission_required('hide_address_page', 'Address Status Update')
def update_status(id):
    """Admin action to update address status via URL parameter (Form data)."""
    # 1. Locate the address or return 404 if not found
    address = Address.query.get_or_404(id)
    
    # 2. Get the new status from the form data
    new_status = request.form.get('status')
    
    # 3. Validate and Update
    if new_status in CommonStatus.__members__:
        address.status = CommonStatus[new_status]
        
        try:
            db.session.commit()
            return jsonify({
                "success": True, 
                "message": f"Address {id} status updated to {new_status}"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "Database error"}), 500
    
    return jsonify({"success": False, "error": "Invalid status value"}), 400