from app import create_app
from app.extensions import mail
from flask_mail import Message

app = create_app()
with app.app_context():
    print(f"Config: MAIL_SERVER={app.config.get('MAIL_SERVER')}, MAIL_PORT={app.config.get('MAIL_PORT')}, MAIL_USE_TLS={app.config.get('MAIL_USE_TLS')}, MAIL_USERNAME={app.config.get('MAIL_USERNAME')}")
    try:
        msg = Message('Test Email', sender=app.config.get('MAIL_DEFAULT_SENDER'), recipients=['saimulhaq09@gmail.com'])
        msg.body = 'This is a test to verify SMTP.'
        mail.send(msg)
        print("Mail sent successfully!", flush=True)
    except Exception as e:
        print(f"Error sending email: {e}", flush=True)
