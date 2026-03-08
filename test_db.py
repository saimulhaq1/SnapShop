from app import create_app, db
from app.models import SalesOrder, Payment, Product

app = create_app()
with app.app_context():
    print("=== SalesOrder Statuses ===")
    res = db.session.execute(db.text("SELECT DISTINCT status FROM sales_order")).fetchall()
    print([r[0] for r in res])
    
    print("=== Payment Statuses ===")
    res2 = db.session.execute(db.text("SELECT DISTINCT status FROM payment")).fetchall()
    print([r[0] for r in res2])
    
    print("=== Product Statuses ===")
    res3 = db.session.execute(db.text("SELECT DISTINCT status FROM product")).fetchall()
    print([r[0] for r in res3])
