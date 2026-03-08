import json
from flask import Flask, session, redirect, url_for, request
from app.extensions import db, migrate 
from app.middleware import init_middleware 

def create_app():
    flask_app = Flask(__name__)
    flask_app.secret_key = "secret-key-123" 

    # Production Config Security
    flask_app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    flask_app.config['TESTING'] = False
    
    # Database Configuration
    database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:12345@localhost/ecommerce')
    
    # Fix Neon connection string for SQLAlchemy
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Connection pool: reuse DB connections instead of creating new ones each request
    flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 280,
        'pool_timeout': 20,
        'max_overflow': 5,
    }

    # Mail Configuration (Uses environment variables, falls back to placeholders)
    flask_app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    flask_app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    flask_app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1']
    flask_app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'test@example.com')
    flask_app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'password')
    flask_app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', flask_app.config['MAIL_USERNAME'])
    
    # ─── Professional URL & Domain Configuration (Amazon-Style Absolute URLs) ───
    # If a SERVER_NAME is provided in the .env (e.g. 'snapshoponline.me'), Flask will strictly use it
    # to generate absolute URLs. We wrap it in a try/except or conditional so local testing still works
    # if it's omitted.
    server_name = os.environ.get('SERVER_NAME')
    if server_name:
        flask_app.config['SERVER_NAME'] = server_name
        
    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    
    from app.extensions import socketio, mail
    mail.init_app(flask_app)
    socketio.init_app(flask_app, cors_allowed_origins="*")

    # Import SocketIO events so they register
    import app.events

    # Register security middleware
    init_middleware(flask_app) 

    # --- 1. INSTANT PERMISSION REFRESH & LOGIN PROTECTION ---
    
    @flask_app.before_request
    def handle_user_access():
        from app.models import Customer
        
        # Public endpoints that don't require login
        public_endpoints = [
            'register_forget.auth_action', 
            'login.login', 
            'login.logout', 
            'static',
            # --- Guest browsing: products & cart ---
            'product.products',
            'product.product_detail',
            'cart.cart_view',
            'cart.remove_from_cart',
            'cart.update_cart',
            'cart.update_qty',
            # Address API (used by profile form)
            'address_api.get_cities',
            'address_api.get_zip_codes',
            # --- Reviews and Auth ---
            'reviews.vote_review',
            'register_forget.reset_password',
            # --- System APIs ---
            'system.mark_notifications_read',
            'system.delete_notification',
        ]
        
        # 1. Avoid redirect loops on public pages
        if request.endpoint in public_endpoints:
            return

        # 2. Redirect unauthenticated users to login (UPDATED ENDPOINT)
        if not session.get('user_id'):
            return redirect(url_for('login.login'))

        # 3. SYNC PERMISSIONS TO SESSION (Instant Refresh Logic)
        user_id = session.get('user_id')
        user_role = session.get('role')

        if user_id and user_role == 'ADMIN':
            # We query the DB to get the latest permission string
            user = Customer.query.get(user_id)
            if user and user.permissions:
                try:
                    # Parse the JSON string from DB
                    new_perms = json.loads(user.permissions)
                    
                    # Handle double-encoded JSON if necessary
                    if isinstance(new_perms, str): 
                        new_perms = json.loads(new_perms)
                    
                    # Store as a dictionary in the session for fast access
                    session['session_user_permissions'] = new_perms
                except Exception:
                    # Fallback to empty dict on parse error
                    session['session_user_permissions'] = {}

    # This makes 'session_user_permissions' available globally in all HTML templates
    @flask_app.context_processor
    def inject_permissions():
        perms = session.get('session_user_permissions', {})
        return dict(session_user_permissions=perms)

    with flask_app.app_context():
        import app.models 

        # --- IMPORT CONTROLLERS ---
        # --- IMPORT CONTROLLERS ---
        from app.controllers.register_forget import auth_bp
        from app.controllers.login import login_bp
        from app.controllers.admin_staff import staff_bp
        from app.controllers.dashboard import dashboard_bp
        from app.controllers.customer import customer_bp
        from app.controllers.complete_profile import shop_bp
        from app.controllers.profile import profile_bp
        from app.controllers.categories import category_registry_bp
        from app.controllers.manage_category import category_editor_bp
        from app.controllers.product import catalog_bp
        from app.controllers.manage_product import inventory_bp
        from app.controllers.cart import cart_bp
        from app.controllers.order import order_bp
        from app.controllers.payment import payment_bp
        from app.controllers.payment_action import payment_action_bp
        from app.controllers.address import address_admin_bp
        from app.controllers.address_api import address_api_bp
        from app.controllers.system import system_bp
        from app.controllers.manage_brand import brand_bp
        from app.controllers.reviews import reviews_bp
        from app.controllers.manage_voucher import voucher_admin_bp
        from app.controllers.manage_banner import banner_bp

        # --- REGISTER BLUEPRINTS WITH EXPLICIT NAMES ---
        flask_app.register_blueprint(auth_bp, name='register_forget')
        flask_app.register_blueprint(login_bp, name='login')
        flask_app.register_blueprint(staff_bp, name='admin_staff')
        flask_app.register_blueprint(dashboard_bp, name='dashboard')
        flask_app.register_blueprint(customer_bp, name='customer')
        flask_app.register_blueprint(shop_bp, name='complete_profile')
        flask_app.register_blueprint(profile_bp, name='profile')
        flask_app.register_blueprint(category_registry_bp, name='categories')
        flask_app.register_blueprint(category_editor_bp, name='manage_category')
        flask_app.register_blueprint(catalog_bp, name='product')
        flask_app.register_blueprint(inventory_bp, name='manage_product')
        flask_app.register_blueprint(brand_bp, name='manage_brand')
        flask_app.register_blueprint(cart_bp, name='cart')
        flask_app.register_blueprint(order_bp, name='order')
        flask_app.register_blueprint(payment_bp, name='payment')
        flask_app.register_blueprint(payment_action_bp, name='payment_action')
        flask_app.register_blueprint(address_admin_bp, name='address')
        flask_app.register_blueprint(address_api_bp, name='address_api')
        flask_app.register_blueprint(system_bp, name='system')
        flask_app.register_blueprint(reviews_bp, name='reviews')
        flask_app.register_blueprint(voucher_admin_bp, name='voucher_admin')
        flask_app.register_blueprint(banner_bp, name='banner_admin')

        # --- REGISTER CLI COMMANDS ---
        from app.utils.cron_jobs import register_commands
        register_commands(flask_app)

    # Wrap the built-in WSGI app with WhiteNoise for serving static files in production
    from whitenoise import WhiteNoise
    flask_app.wsgi_app = WhiteNoise(flask_app.wsgi_app, root='app/static/', prefix='static/')

    return flask_app