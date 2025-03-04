from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Remplacez par une clé secrète sécurisée

# Fonction pour obtenir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('baselocale.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialiser les données utilisateur dans la session
def init_user_session():
    if 'user' not in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM profile WHERE id = 1').fetchone()
        if user is None:
            flash('Utilisateur non trouvé dans la base de données.', 'error')
            return redirect(url_for('index'))
        session['user'] = {
            'photo_profil': 'static/src/images/profile_icon_default.png',
            'nom': user['nom'],
            'prenom': user['prenom'],
            'email': user['email'],
            'statut': user['statut']
        }
        conn.close()

@app.route('/')
def index():
    return render_template('acceuil.html')

@app.route('/profile')
def profile():
    init_user_session()
    if 'user' not in session:
        return redirect(url_for('index'))
    user = session['user']
    badges = [
        {'image_url': 'static/src/images/badge_graine_de_champion.png', 'nom': 'Badge 1'},
        {'image_url': 'static/src/images/badge_gardien_de_potager.png', 'nom': 'Badge 2'}
    ]
    return render_template('profile.html', user=user, badges=badges)

@app.route('/acceuil')
def acceuil():
    return render_template('acceuil.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    init_user_session()
    if 'user' not in session:
        return redirect(url_for('index'))
    user = session['user']
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        statut = request.form['statut']
        
        conn = get_db_connection()
        
        # Vérifier si un utilisateur avec le même nom/prénom ou email existe déjà
        existing_user = conn.execute('SELECT * FROM profile WHERE (nom = ? AND prenom = ?) OR email = ? AND id != 1',
                                     (nom, prenom, email)).fetchone()
        if existing_user:
            flash('Un utilisateur avec le même nom/prénom ou email existe déjà.', 'error')
            conn.close()
            return redirect(url_for('edit_profile'))
        
        conn.execute('UPDATE profile SET nom = ?, prenom = ?, email = ?, statut = ? WHERE id = 1',
                     (nom, prenom, email, statut))
        conn.commit()
        conn.close()
        
        user['nom'] = nom
        user['prenom'] = prenom
        user['email'] = email
        user['statut'] = statut
        session['user'] = user  # Mettre à jour les données utilisateur dans la session
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM profile WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'photo_profil': 'static/src/images/profile_icon_default.png',
                'nom': user['nom'],
                'prenom': user['prenom'],
                'email': user['email'],
                'statut': user['statut']
            }
            return redirect(url_for('profile'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        
        # Vérifier si un utilisateur avec le même email existe déjà
        existing_user = conn.execute('SELECT * FROM profile WHERE email = ?', (email,)).fetchone()
        if existing_user:
            flash('Un utilisateur avec cet email existe déjà.', 'error')
            conn.close()
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        conn.execute('INSERT INTO profile (nom, prenom, email, password, statut) VALUES (?, ?, ?, ?, ?)',
                     (nom, prenom, email, hashed_password, 'Membre'))
        conn.commit()
        conn.close()
        
        flash('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    # Logique pour la déconnexion
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)