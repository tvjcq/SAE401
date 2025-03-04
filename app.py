# python
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, UserMixin, current_user
)

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # nécessaire pour utiliser les sessions

# Configuration de la base de données avec SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuration de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modèle utilisateur
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    nom = db.Column(db.String(150), nullable=False)
    prenom = db.Column(db.String(150), nullable=False)
    statut = db.Column(db.String(150), nullable=False)

# Création de la base de données si elle n'existe pas
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.prenom)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

# python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        statut = request.form.get('statut')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Cet email est déjà utilisé")
        new_user = User(email=email, password=password, nom=nom, prenom=prenom, statut=statut)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)