from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Remplacez par une clé secrète sécurisée

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

@app.route('/profile')
@login_required
def profile():
    badges = [
        {'image_url': 'static/src/images/badge_graine_de_champion.png', 'nom': 'Badge 1'},
        {'image_url': 'static/src/images/badge_gardien_de_potager.png', 'nom': 'Badge 2'}
    ]
    return render_template('profile.html', user=current_user, badges=badges)

@app.route('/acceuil')
def acceuil():
    return render_template('acceuil.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.nom = request.form['nom']
        current_user.prenom = request.form['prenom']
        current_user.email = request.form['email']
        current_user.statut = request.form['statut']
        
        db.session.commit()
        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('acceuil'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
            return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        statut = request.form.get('statut')
        if User.query.filter_by(email=email).first():
            flash('Un utilisateur avec cet email existe déjà.', 'error')
            return render_template('register.html', error="Cet email est déjà utilisé")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password, nom=nom, prenom=prenom, statut=statut)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('acceuil'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/etage_0')
def etage_0():
    return render_template('etage_0.html')

@app.route('/etage_1')
def etage_1():
    return render_template('etage_1.html')

@app.route('/etage_2')
def etage_2():
    return render_template('etage_2.html')

if __name__ == '__main__':
    app.run(debug=True)