from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, UserMixin, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

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
    last_name = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(150), nullable=False)
    
    # Relation: one user peut posséder plusieurs jardins
    jardins = db.relationship('Jardin', backref='proprietaire', lazy=True)
    # Relation: one user a plusieurs votes
    votes = db.relationship('Vote', backref='user', lazy=True)

# Modèle Jardin
class Jardin(db.Model):
    __tablename__ = 'jardins'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'interieur' ou 'exterieur'

    # Relation avec les slots
    slots = db.relationship('SlotJardin', backref='jardin', lazy=True)

# Modèle Legume
class Legume(db.Model):
    __tablename__ = 'legumes'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relation avec les slots
    slots = db.relationship('SlotJardin', backref='legume', lazy=True)

# Modèle SlotJardin
class SlotJardin(db.Model):
    __tablename__ = 'slots_jardin'
    id = db.Column(db.Integer, primary_key=True)
    jardin_id = db.Column(db.Integer, db.ForeignKey('jardins.id'), nullable=False)
    legume_id = db.Column(db.Integer, db.ForeignKey('legumes.id'), nullable=False)
    position = db.Column(db.String(50), nullable=False)

    # Relation avec les votes
    votes = db.relationship('Vote', backref='slot_jardin', lazy=True)

# Modèle Vote
class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_jardin_id = db.Column(db.Integer, db.ForeignKey('slots_jardin.id'), nullable=False)
    vote = db.Column(db.Integer, nullable=False)

# Modèle Quiz
class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    # Relation vers les questions du quiz
    questions = db.relationship('Question', backref='quiz', lazy=True)

# Modèle Question
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

    # Relation vers les choix pour cette question
    choices = db.relationship('Choice', backref='question', lazy=True)

# Modèle Choice (Choix)
class Choice(db.Model):
    __tablename__ = 'choices'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(150), nullable=False)
    is_right = db.Column(db.Boolean, nullable=False)

# Création de la base de données si elle n'existe pas
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    quizzes = Quiz.query.all()
    return render_template('index.html', name=current_user.first_name, quizzes=quizzes)

@app.route('/profile')
@login_required
def profile():
    badges = [
        {'image_url': 'static/src/images/badge_graine_de_champion.png', 'nom': 'Badge 1'},
        {'image_url': 'static/src/images/badge_gardien_de_potager.png', 'nom': 'Badge 2'}
    ]
    return render_template('profile.html', user=current_user, badges=badges)

@app.route('/accueil')
def accueil():
    return render_template('accueil.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.last_name = request.form['last_name']
        current_user.first_name = request.form['first_name']
        current_user.email = request.form['email']
        current_user.status = request.form['status']
        
        db.session.commit()
        return render_template('profile.html', user=current_user, update_message="Profil mis à jour avec succès")
    return render_template('edit_profile.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        status = request.form.get('status')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Cet email est déjà utilisé")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password, last_name=last_name, first_name=first_name, status=status)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('accueil'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route pour afficher l'introduction du quiz
@app.route('/quiz/<int:quiz_id>')
@login_required
def quiz_intro(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    session['quiz_id'] = quiz.id  # store quiz_id for later use
    session['quiz_score'] = 0
    session['quiz_total'] = len(quiz.questions)
    session['current_question'] = 0
    return render_template('quiz_intro.html', quiz=quiz)

# Route pour traiter chaque question
@app.route('/quiz/<int:quiz_id>/question', methods=['GET', 'POST'])
@login_required
def quiz_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    curr_index = session.get('current_question', 0)
    questions = quiz.questions
    # If all questions are answered, redirect to result
    if curr_index >= len(questions):
        return redirect(url_for('quiz_result', quiz_id=quiz.id))
    question = questions[curr_index]
    
    if request.method == 'POST':
        try:
            chosen_choice_id = int(request.form.get('choice'))
        except (ValueError, TypeError):
            chosen_choice_id = None
        
        chosen_choice = next((c for c in question.choices if c.id == chosen_choice_id), None)
        correct = chosen_choice.is_right if chosen_choice else False
        if correct:
            session['quiz_score'] += 1
        
        feedback = {
            'selected': chosen_choice_id,
            'correct': correct,
            'correct_id': next((c.id for c in question.choices if c.is_right), None)
        }
        # Do NOT increment session['current_question'] here.
        return render_template('quiz_question.html', quiz=quiz, question=question, feedback=feedback)
    
    return render_template('quiz_question.html', quiz=quiz, question=question, feedback=None)

@app.route('/quiz/<int:quiz_id>/next')
@login_required
def quiz_next(quiz_id):
    session['current_question'] = session.get('current_question', 0) + 1
    return redirect(url_for('quiz_question', quiz_id=quiz_id))

# Route pour afficher le résultat du quiz
@app.route('/quiz/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = session.get('quiz_score', 0)
    total = session.get('quiz_total', len(quiz.questions))
    # Définir un titre et un message simples en fonction du score
    if score == total:
        title = "Bravo!"
        description = "Excellent, toutes les questions sont correctes."
    elif score >= total / 2:
        title = "Bon début"
        description = "Bon travail, il y a encore de quoi s'améliorer."
    else:
        title = "Peut mieux faire"
        description = "Continuez à pratiquer !"
    return render_template('quiz_result.html', score=score, total=total, title=title, description=description)

@app.route('/jardin/<int:jardin_id>')
@login_required
def jardin_detail(jardin_id):
    jardin = Jardin.query.get_or_404(jardin_id)
    return render_template('jardin.html', jardin=jardin)

@app.route('/legume/<int:legume_id>')
@login_required
def legume_detail(legume_id):
    legume = Legume.query.get_or_404(legume_id)
    return render_template('legume.html', legume=legume)

@app.route('/vote/<int:slot_id>', methods=['GET', 'POST'])
@login_required
def vote_slot(slot_id):
    slot = SlotJardin.query.get_or_404(slot_id)
    if request.method == 'POST':
        try:
            vote_value = int(request.form.get('vote'))
        except (ValueError, TypeError):
            vote_value = 0
        new_vote = Vote(user_id=current_user.id, slot_jardin_id=slot.id, vote=vote_value)
        db.session.add(new_vote)
        db.session.commit()
        return redirect(url_for('jardin_detail', jardin_id=slot.jardin_id))
    return render_template('vote.html', slot=slot)

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