from app import create_app, db
from app.models import Customer
app = create_app()
with app.app_context():
    res = db.session.execute(db.text("SELECT DISTINCT role FROM customer")).fetchall()
    print([r[0] for r in res])
