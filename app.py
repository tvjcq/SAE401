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
        return redirect(url_for('index'))
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
    # Si toutes les questions ont été traitées, aller au résultat
    if curr_index >= len(questions):
        return redirect(url_for('quiz_result', quiz_id=quiz.id))
    question = questions[curr_index]
    
    if request.method == 'POST':
        # Récupérer l'identifiant du choix soumis
        try:
            chosen_choice_id = int(request.form.get('choice'))
        except (ValueError, TypeError):
            chosen_choice_id = None
        
        # Vérifier si le choix sélectionné est correct
        chosen_choice = next((c for c in question.choices if c.id == chosen_choice_id), None)
        correct = chosen_choice.is_right if chosen_choice else False
        if correct:
            session['quiz_score'] += 1
        
        feedback = {
            'selected': chosen_choice_id,
            'correct': correct,
            'correct_id': next((c.id for c in question.choices if c.is_right), None)
        }
        # Passer à la question suivante pour la prochaine requête
        session['current_question'] = curr_index + 1
        return render_template('quiz_question.html', quiz=quiz, question=question, feedback=feedback)
    
    return render_template('quiz_question.html', quiz=quiz, question=question, feedback=None)

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
        description = "Bon travail, il y a encore de la place pour s'améliorer."
    else:
        title = "Peut mieux faire"
        description = "Continuez à pratiquer !"
    return render_template('quiz_result.html', score=score, total=total, title=title, description=description)

if __name__ == '__main__':
    app.run(debug=True)