# createadmin.py
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

admin = User(
    username="admin",
    email="admin@example.com",
    password=generate_password_hash("adminpass"),
    role="admin"
)
db.session.add(admin)
db.session.commit()
print("Admin account created: Username: admin, Password: adminpass")
