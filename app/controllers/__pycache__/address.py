from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
import app.models as models

address_bp = Blueprint('address', __name__)

@address_bp.route('/address')
def addresses():
    q = request.args.get('q', '')
    search_type = request.args.get('search_type', 'address')
    status = request.args.get('status', '')
    direction = request.args.get('direction', 'asc')

    query = models.Address.query.outerjoin(models.ZipCode).outerjoin(
        models.City).outerjoin(models.Customer)

    if q:
        query = query.filter(models.Address.address.ilike(f'%{q}%'))

    if status in models.CommonStatus.__members__:
        query = query.filter(models.Address.status == models.CommonStatus[status])

    query = query.order_by(
        models.Address.address_id.asc() if direction == 'asc'
        else models.Address.address_id.desc()
    )

    return render_template('address.html', addresses=query.all(), models=models)


@address_bp.route('/address/update_status/<int:id>', methods=['POST'])
def update_address_status(id):
    address = models.Address.query.get_or_404(id)
    status = request.form.get('status')

    if status in models.CommonStatus.__members__:
        address.status = models.CommonStatus[status]
        address.updated_at = datetime.now()
        models.db.session.commit()
        return jsonify(success=True)

    return jsonify(success=False), 400


@address_bp.route('/address/delete/<int:id>', methods=['POST'])
def delete_address(id):
    address = models.Address.query.get_or_404(id)
    models.db.session.delete(address)
    models.db.session.commit()
    flash("Address deleted", "success")
    return redirect(url_for('address.addresses'))
