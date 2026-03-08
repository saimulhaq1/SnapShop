from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.customer_model import Customer
from app.models.enums import CommonStatus
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from app.extensions import db, mail
from flask import current_app
from datetime import datetime

# Shared serializer helper
def _get_serializer():
    return URLSafeTimedSerializer(current_app.secret_key)

# ─── Send verification email ──────────────────────────────────────────
def send_verification_email(user):
    s = _get_serializer()
    token = s.dumps(user.email, salt='email-confirm-salt')

    # Store token hash in DB (for one-time-use invalidation)
    user.verify_token = token
    user.verify_expiry = datetime.utcnow()
    db.session.commit()

    # Force the correct localhost port for testing if running locally
    verify_link = url_for('register_forget.verify_email', token=token, _external=True)
    if '127.0.0.1' in verify_link and ':5000' not in verify_link:
        verify_link = verify_link.replace('127.0.0.1', '127.0.0.1:5000')
    elif 'localhost' in verify_link and ':5000' not in verify_link:
        verify_link = verify_link.replace('localhost', '127.0.0.1:5000')

    try:
        msg = Message(
            subject='Confirm Your Email — SnapShop',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        msg.html = render_template('email/verify_email.html', user=user, verify_link=verify_link)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Email Error] {e}")
        return False

# This variable is imported in __init__.py as auth_bp
auth_bp = Blueprint('register_forget', __name__)

@auth_bp.route('/auth-action/<mode>', methods=['GET', 'POST'])
def auth_action(mode):
    if request.method == 'POST':
        if mode == 'register':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')

            if password != confirm:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('register_forget.auth_action', mode='register'))

            if Customer.query.filter_by(email=email).first():
                flash("Email already registered.", "warning")
                return redirect(url_for('register_forget.auth_action', mode='register'))

            new_user = Customer(
                name=username,
                email=email,
                password=generate_password_hash(password),
                role='CUSTOMER',
                # ⚠️ INACTIVE until email is verified
                status=CommonStatus.INACTIVE,
                permissions='{}'
            )

            db.session.add(new_user)
            db.session.commit()

            # Send verification email
            sent = send_verification_email(new_user)
            if sent:
                flash(
                    f"Account created! A verification link has been sent to <strong>{email}</strong>. "
                    "Please check your inbox (and spam folder) to activate your account.",
                    "info"
                )
            else:
                flash(
                    "Account created but we couldn't send the verification email. "
                    "Please contact support.",
                    "warning"
                )

            return redirect(url_for('register_forget.verification_pending', email=email))

        elif mode == 'forgot':
            email = request.form.get('email')
            user = Customer.query.filter_by(email=email).first()

            if user:
                s = _get_serializer()
                token = s.dumps(email, salt='password-reset-salt')
                reset_link = url_for('register_forget.reset_password', token=token, _external=True)

                try:
                    msg = Message(
                        'SnapShop Password Reset',
                        sender=current_app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[email]
                    )
                    msg.body = f'''To reset your password, visit the following link:
{reset_link}

If you did not make this request, simply ignore this email.
This link expires in 30 minutes.
'''
                    mail.send(msg)
                    flash(f"Reset instructions sent to {email}.", "info")
                except Exception as e:
                    print(f"[Email Error] {e}")
                    flash("Error sending email. Please try again later.", "danger")
            else:
                flash("If the email is registered, reset instructions will be sent.", "info")

            return redirect(url_for('login.login'))

    return render_template('register_forget.html', mode=mode)


# ─── Email Verification Route ─────────────────────────────────────────
@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    s = _get_serializer()
    try:
        # Token expires in 3600s = 1 hour
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)
    except SignatureExpired:
        flash("Activation link has expired. Please request a new one.", "danger")
        return redirect(url_for('register_forget.resend_verification'))
    except BadSignature:
        flash("Invalid activation link.", "danger")
        return redirect(url_for('login.login'))

    user = Customer.query.filter_by(email=email).first()

    if not user:
        flash("Account not found.", "danger")
        return redirect(url_for('register_forget.auth_action', mode='register'))

    # One-time-use: check token still matches (not already used)
    if user.verify_token != token:
        flash("This verification link has already been used.", "warning")
        return redirect(url_for('login.login'))

    # Activate the account
    user.status = CommonStatus.ACTIVE
    user.verify_date = datetime.utcnow()
    user.verify_token = None  # Invalidate token so it cannot be reused
    db.session.commit()

    # Auto-login after verification
    session.clear()
    session['user_id'] = user.customer_id
    session['username'] = user.name
    session['role'] = user.role.value if hasattr(user.role, 'value') else user.role
    session['session_user_permissions'] = {}

    flash(f"Welcome, {user.name}! Your email has been verified and you are now logged in.", "success")
    return redirect(url_for('product.products'))


# ─── Resend Verification Email Route ──────────────────────────────────
@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
    else:
        email = request.args.get('email', '').strip()
    if not email:
        flash("No email address provided.", "danger")
        return redirect(url_for('login.login'))

    user = Customer.query.filter_by(email=email).first()
    if not user:
        # Don't reveal account existence
        flash("If that email is registered, a new verification link has been sent.", "info")
        return redirect(url_for('login.login'))

    if user.status == CommonStatus.ACTIVE:
        flash("Your account is already verified. Please log in.", "info")
        return redirect(url_for('login.login'))

    sent = send_verification_email(user)
    if sent:
        flash(f"A new verification link has been sent to <strong>{email}</strong>.", "info")
    else:
        flash("Failed to send email. Please try again later.", "danger")

    return redirect(url_for('login.login'))


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        # 1800 seconds = 30 minutes
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except Exception:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for('register_forget.auth_action', mode='forgot'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register_forget.reset_password', token=token))

        user = Customer.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash("Your password has been updated! You can now log in.", "success")
            return redirect(url_for('login.login'))

    return render_template('reset_password.html', token=token)


# ─── Verification Pending Page ──────────────────────────────────────────
@auth_bp.route('/verification-pending')
def verification_pending():
    email = request.args.get('email')
    return render_template('verification_pending.html', email=email)