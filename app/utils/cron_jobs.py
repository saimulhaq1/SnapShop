import click
from datetime import datetime, timedelta
from flask.cli import with_appcontext
from app.models import db, Cart, Customer
from app.extensions import mail
from flask_mail import Message
from flask import current_app

@click.command('recover_abandoned_carts')
@with_appcontext
def recover_abandoned_carts():
    """Identify carts older than 7 days and send reminder emails."""
    current_app.logger.info("Starting Abandoned Cart Recovery job...")
    
    # 7 days ago
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    # We want unique customers who have items in their cart added before the cutoff date
    # Normally we'd track a specific `updated_at` on the cart, but `added_at` works for our schema
    abandoned_carts = db.session.query(Cart.customer_id).filter(
        Cart.added_at <= cutoff_date
    ).distinct().all()

    if not abandoned_carts:
        current_app.logger.info("No abandoned carts found.")
        return

    emails_sent = 0
    for result in abandoned_carts:
        customer_id = result[0]
        customer = Customer.query.get(customer_id)
        
        if customer and customer.email:
            # Send Email
            msg = Message(
                subject='You left something behind! 🛒',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[customer.email]
            )
            msg.body = f'''Hi {customer.name},

We noticed you left some amazing items in your shopping cart! 
They are selling out fast. Jump back in and complete your checkout before they are gone!

Click here to return to your cart: http://127.0.0.1:5000/cart

Best regards,
SnapShop Team
'''
            try:
                mail.send(msg)
                emails_sent += 1
            except Exception as e:
                current_app.logger.error(f"Failed to send cart recovery email to {customer.email}: {e}")

    current_app.logger.info(f"Abandoned Cart Recovery job completed. Sent {emails_sent} emails.")

def register_commands(app):
    app.cli.add_command(recover_abandoned_carts)
