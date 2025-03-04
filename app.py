from flask import Flask, render_template
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
        {'image_url': 'static/src/images/badge1.png', 'nom': 'Badge 1'},
        {'image_url': 'static/src/images/badge2.png', 'nom': 'Badge 2'}
    ]
    return render_template('profile.html', user=user, badges=badges)

@app.route('/acceuil')
def acceuil():
    return render_template('acceuil.html')

if __name__ == '__main__':
    app.run(debug=True)
