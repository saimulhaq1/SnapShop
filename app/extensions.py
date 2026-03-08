from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_socketio import SocketIO
from flask_mail import Mail

# Updated naming convention: Removed referred_table_name to prevent IndexError
# MySQL still gets a unique, explicit name for every constraint.
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s", 
    "pk": "pk_%(table_name)s"
}

# Apply it to metadata
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
socketio = SocketIO()
mail = Mail()