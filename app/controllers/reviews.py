from flask import Blueprint, request, redirect, url_for, flash, session, jsonify, render_template
from sqlalchemy.exc import IntegrityError
from app.models import db, ProductReview, VoteTracking, Product, Notification
from app.extensions import socketio
from app.models.customer_model import Customer
from app.middleware import admin_permission_required

reviews_bp = Blueprint('reviews', __name__)


def _get_avg_rating(product_id):
    """Compute the average star rating for a product from top-level reviews."""
    top_reviews = ProductReview.query.filter_by(
        product_id=product_id, parent_id=None
    ).filter(ProductReview.rating.isnot(None)).all()

    if not top_reviews:
        return None, 0
    avg = sum(r.rating for r in top_reviews) / len(top_reviews)
    return round(avg, 1), len(top_reviews)


# ---------------------------------------------------------------------------
# POST /reviews/add  — Submit a new review or reply
# ---------------------------------------------------------------------------
@reviews_bp.route('/reviews/add', methods=['POST'])
def add_review():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please Login or Create an Account to leave a review.", "warning")
        return redirect(url_for('login.login'))

    product_id = request.form.get('product_id', type=int)
    parent_id = request.form.get('parent_id', type=int)
    comment = request.form.get('comment', '').strip()
    rating_str = request.form.get('rating')

    if not comment:
        flash("Comment cannot be empty.", "warning")
        return redirect(request.referrer or url_for('product.products'))

    # Rating is only required on top-level reviews
    rating = None
    if parent_id is None:
        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            flash("Please select a star rating (1–5) before submitting.", "warning")
            return redirect(request.referrer or url_for('product.products'))

    review = ProductReview(
        product_id=product_id,
        customer_id=user_id,
        parent_id=parent_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    
    # Notify Admin Real-Time
    user = Customer.query.get(user_id)
    product = Product.query.get(product_id)
    if not parent_id:  # Only notify on top-level reviews
        notif = Notification(
            recipient_role='ADMIN',
            type='REVIEW',
            title=f'New SnapShop Feedback: {product.name if product else "Product"}',
            message=f"{user.name if user else 'A customer'} left a {rating}-star review.",
            link=url_for('reviews.manage_reviews')
        )
        db.session.add(notif)
        db.session.commit()
        socketio.emit('admin_alert', {
            'type': 'REVIEW',
            'title': notif.title,
            'message': notif.message,
            'link': notif.link
        }, room='admin_room')
    else:
        # Notify Original Reviewer of the Reply
        parent_review = ProductReview.query.get(parent_id)
        if parent_review and parent_review.customer_id != user_id:  # Don't notify if replying to oneself
            reply_notif = Notification(
                user_id=parent_review.customer_id,
                recipient_role='CUSTOMER',
                type='REVIEW_REPLY',
                title='SnapShop Reply to Your Review',
                message=f"{user.name if user else 'Someone'} replied to your review on {product.name if product else 'a product'}.",
                link=url_for('product.product_detail', id=product_id) + '#reviews'
            )
            db.session.add(reply_notif)
            db.session.commit()
            
            socketio.emit('customer_alert', {
                'type': 'REVIEW_REPLY',
                'title': reply_notif.title,
                'message': reply_notif.message,
                'link': reply_notif.link
            }, room=f'user_{parent_review.customer_id}')

    if parent_id:
        flash("Reply posted successfully!", "success")
    else:
        flash("Your review has been submitted!", "success")

    if request.form.get('redirect_to') == 'manage_reviews':
        return redirect(url_for('reviews.manage_reviews'))

    return redirect(url_for('product.product_detail', id=product_id))


# ---------------------------------------------------------------------------
# POST /reviews/vote/<review_id>  — Like or Dislike
# ---------------------------------------------------------------------------
@reviews_bp.route('/reviews/vote/<int:review_id>', methods=['POST'])
def vote_review(review_id):
    user_id = session.get('user_id')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or (request.content_type and 'application/json' in request.content_type)
    
    if not user_id:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Please Login to vote.', 'redirect': url_for('login.login')}), 401
        flash("Please Login or Create an Account to vote.", "warning")
        return redirect(url_for('login.login'))

    vote_type = request.form.get('vote_type') if not request.is_json else request.json.get('vote_type')
    if vote_type not in ('like', 'dislike'):
        if is_ajax: return jsonify(success=False, message="Invalid vote type."), 400
        flash("Invalid vote type.", "danger")
        return redirect(request.referrer or url_for('product.products'))

    review = ProductReview.query.get_or_404(review_id)

    # Check if user already voted
    existing = VoteTracking.query.filter_by(
        review_id=review_id, customer_id=user_id
    ).first()

    current_user_vote = None

    if existing:
        if existing.vote_type == vote_type:
            # Same vote → toggle off (remove)
            db.session.delete(existing)
            db.session.commit()
            if not is_ajax: flash("Vote removed.", "info")
            current_user_vote = None
        else:
            # Different vote → switch it
            existing.vote_type = vote_type
            db.session.commit()
            if not is_ajax: flash("Vote updated.", "success")
            current_user_vote = vote_type
    else:
        new_vote = VoteTracking(
            review_id=review_id,
            customer_id=user_id,
            vote_type=vote_type
        )
        db.session.add(new_vote)
        try:
            db.session.commit()
            current_user_vote = vote_type
        except IntegrityError:
            db.session.rollback()
            if not is_ajax: flash("You have already voted on this review.", "info")

    if is_ajax:
        return jsonify({
            'success': True,
            'like_count': review.like_count(),
            'dislike_count': review.dislike_count(),
            'user_vote': current_user_vote
        })

    return redirect(url_for('product.product_detail', id=review.product_id))


# ---------------------------------------------------------------------------
# POST /reviews/delete/<review_id>  — Admin or Author delete
# ---------------------------------------------------------------------------
@reviews_bp.route('/reviews/delete/<int:review_id>', methods=['GET', 'POST'])
def delete_review(review_id):
    user_id = session.get('user_id')
    role = session.get('role')
    
    if not user_id:
        flash("Please Login or Create an Account to delete a review.", "warning")
        return redirect(url_for('login.login'))

    review = ProductReview.query.get_or_404(review_id)
    product_id = review.product_id

    # Allow admins to delete any review, or authors to delete their own review
    if role != 'ADMIN' and user_id != review.customer_id:
        flash("Unauthorized: You can only delete your own reviews.", "danger")
        return redirect(request.referrer or url_for('product.products'))

    db.session.delete(review)
    db.session.commit()

    flash("Review deleted successfully.", "success")
    if request.form.get('redirect_to') == 'manage_reviews':
        return redirect(url_for('reviews.manage_reviews'))

    return redirect(request.referrer or url_for('product.product_detail', id=product_id))


# ---------------------------------------------------------------------------
# GET /admin/reviews  — Admin Review Management Dashboard
# ---------------------------------------------------------------------------
@reviews_bp.route('/admin/reviews', methods=['GET'])
@admin_permission_required('hide_reviews_page', 'Product Feedback')
def manage_reviews():
    if session.get('role') != 'ADMIN':
        flash("Unauthorized: Admin access required.", "danger")
        return redirect(url_for('product.products'))

    # Fetch all reviews, ordered by newest first
    all_reviews = ProductReview.query.order_by(ProductReview.created_at.desc()).all()
    
    # Calculate rating summary per product (from top-level reviews only)
    products = Product.query.all()
    product_summaries = {}
    for p in products:
        avg, cnt = _get_avg_rating(p.pro_id)
        if cnt > 0:
            product_summaries[p.pro_id] = {'avg': avg, 'count': cnt, 'name': p.name}
            
    return render_template(
        'manage_reviews.html', 
        reviews=all_reviews, 
        product_summaries=product_summaries
    )
