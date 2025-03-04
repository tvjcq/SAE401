from flask import Flask, render_template, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('acceuil.html')

@app.route('/profile')
def profile():
    user = {
        'photo_profil': 'static/src/images/profile_icon_default.png',
        'nom': 'Doe',
        'prenom': 'John',
        'email': 'john.doe@example.com',
        'statut': 'Membre'
    }
    badges = [
        {'image_url': 'static/src/images/badge_graine_de_champion.png', 'nom': 'Badge 1'},
        {'image_url': 'static/src/images/badge_gardien_de_potager.png', 'nom': 'Badge 2'}
    ]
    return render_template('profile.html', user=user, badges=badges)

@app.route('/acceuil')
def acceuil():
    return render_template('acceuil.html')


@app.route('/edit_profile')
def edit_profile():
    # Logique pour la page de modification du profil
    return "Page de modification du profil"

@app.route('/logout')
def logout():
    # Logique pour la déconnexion
    return "Déconnexion réussie"

if __name__ == '__main__':
    app.run(debug=True)
