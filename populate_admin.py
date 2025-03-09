from app import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    admin_email = 'admin@example.com'
    if not User.query.filter_by(email=admin_email).first():
        admin_user = User(
            email=admin_email,
            password=generate_password_hash('admin_password', method='pbkdf2:sha256'),
            last_name='Admin',
            first_name='Admin',
            status='Administrateur',
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Compte admin créé :", admin_email)
    else:
        print("Le compte admin existe déjà :", admin_email)