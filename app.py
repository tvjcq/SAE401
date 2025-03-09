from flask import Flask, render_template, request, redirect, url_for, session, abort
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, UserMixin, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from dotenv import load_dotenv
import os
import requests

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
    seeds = db.Column(db.Integer, default=10, nullable=False)
    status = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
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
    legume_id = db.Column(db.Integer, db.ForeignKey('legumes.id'), nullable=True)  # autorise None pour un slot vide
    position = db.Column(db.String(50), nullable=False)

    # Relation avec les votes
    votes = db.relationship('Vote', backref='slot_jardin', lazy=True)

# Modèle Vote
# language: python
class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_jardin_id = db.Column(db.Integer, db.ForeignKey('slots_jardin.id'), nullable=False)
    legume_id = db.Column(db.Integer, db.ForeignKey('legumes.id'), nullable=False)

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
    
# Modèle Message de la communauté
class CommunityMessage(db.Model):
    __tablename__ = 'community_messages'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default="message")
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    
class Poll(db.Model):
    __tablename__ = 'polls'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150), nullable=False)
    question = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    options = db.relationship('PollOption', backref='poll', lazy=True)

class PollOption(db.Model):
    __tablename__ = 'poll_options'
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False)
    option_text = db.Column(db.String(150), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_votes = db.relationship('PollVote', backref='poll_option', lazy=True)

class PollVote(db.Model):
    __tablename__ = 'poll_votes'
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_option_id = db.Column(db.Integer, db.ForeignKey('poll_options.id'), nullable=False)

# Création de la base de données si elle n'existe pas
with app.app_context():
    db.create_all()
    
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.first_name)

@app.route('/profile')
@login_required
def profile():
    badges = [
        {'image_url': 'static/src/images/badge_graine_de_champion.png', 'nom': 'Badge 1'},
        {'image_url': 'static/src/images/badge_gardien_de_potager.png', 'nom': 'Badge 2'}
    ]
    return render_template('profile.html', user=current_user, badges=badges)

@app.route('/weather_data')
def weather_data():
    url = "https://api.open-meteo.com/v1/forecast?latitude=43.3412&longitude=3.214&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&forecast_days=1"
    response = requests.get(url)
    weather_data = response.json()
    current_weather = weather_data['current']
    return current_weather

@app.route('/accueil')
def accueil():
    quizzes = Quiz.query.all()
    url = "https://api.open-meteo.com/v1/forecast?latitude=43.3412&longitude=3.214&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&forecast_days=1"
    response = requests.get(url)
    weather_data = response.json()
    current_weather = weather_data['current']
    return render_template('accueil.html', weather=current_weather, quizzes=quizzes)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.last_name = request.form['last_name']
        current_user.first_name = request.form['first_name']
        current_user.email = request.form['email']
        current_user.status = request.form['status']
        
        db.session.commit()
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
            return redirect(url_for('accueil'))
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
            current_user.seeds += 2
            db.session.commit()
        
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
    existing_vote = Vote.query.filter_by(user_id=current_user.id, slot_jardin_id=slot.id).first()
    if existing_vote:
        message = "Vous avez déjà voté pour ce slot. Vous ne pouvez pas le modifier."
        return render_template('vote.html', slot=slot, message=message, already_voted=True)
    
    legumes = Legume.query.all()  # Récupérer tous les légumes
    if request.method == 'POST':
        try:
            legume_vote = int(request.form.get('vote'))
        except (ValueError, TypeError):
            legume_vote = 0
        new_vote = Vote(user_id=current_user.id, slot_jardin_id=slot.id, legume_id=legume_vote)
        db.session.add(new_vote)
        db.session.commit()
        return redirect(url_for('jardin_detail', jardin_id=slot.jardin_id))
    
    return render_template('vote.html', slot=slot, already_voted=False, legumes=legumes)

@app.route('/plantid', methods=['GET', 'POST'])
def plant_id():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return render_template('plantid.html', error="Aucune image détectée.")
        photo = request.files['photo']
        if photo.filename == '':
            return render_template('plantid.html', error="Aucune image sélectionnée.")
        
        # Vérifier que l'extension est autorisée
        allowed_extensions = {'jpeg', 'jpg', 'png'}
        filename = photo.filename.lower()
        if not ('.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions):
            return render_template('plantid.html', error="Format d'image non supporté. Veuillez utiliser un format jpeg, jpg ou png.")
        
        api_url = "https://my-api.plantnet.org/v2/identify/all"
        params = {
            "include-related-images": "false",
            "no-reject": "false",
            "nb-results": "1",
            "lang": "fr",
            "api-key": os.getenv('PLANTNET_API_KEY')
        }
        files = {
            'images': (photo.filename, photo.stream, photo.mimetype)
        }
        headers = {
            'accept': 'application/json'
        }
        
        response = requests.post(api_url, params=params, files=files, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                species = results[0].get('species', {})
                common_names = species.get('commonNames', [])
                plant_common_name = common_names[0] if common_names else 'Inconnu'
            else:
                plant_common_name = 'Inconnu'
            return render_template('plantid.html', plant_name=plant_common_name)
        else:
            return render_template('plantid.html', error="Erreur lors de l'identification (code {}).".format(response.status_code))
    return render_template('plantid.html')

@app.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    if request.method == 'POST' and current_user.is_admin:
        new_message = request.form.get('message')
        message_type = request.form.get('type', 'message')
        if new_message:
            msg = CommunityMessage(
                author=current_user.first_name,
                content=new_message,
                type=message_type
            )
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('community'))
    messages = CommunityMessage.query.order_by(CommunityMessage.timestamp).all()
    polls = Poll.query.order_by(Poll.timestamp.desc()).all()
    quizzes = Quiz.query.order_by(Quiz.id.desc()).all()
    
    # Calculer si l'utilisateur a voté pour chaque sondage
    for poll in polls:
        poll.has_voted = PollVote.query.filter_by(poll_id=poll.id, user_id=current_user.id).first() is not None
        # Calcul du total de votes pour faciliter le calcul des pourcentages
        poll.total_votes = sum(opt.votes for opt in poll.options)
        
    return render_template('community.html', messages=messages, polls=polls, quizzes=quizzes)
# language: python
@app.route('/create_poll', methods=['GET', 'POST'])
@login_required
@admin_required
def create_poll():
    if request.method == 'POST':
        question = request.form.get('question')
        options = request.form.getlist('option')  # plusieurs options sont envoyées
        if question and options:
            poll = Poll(author=current_user.first_name, question=question)
            db.session.add(poll)
            db.session.flush()  # pour obtenir poll.id
            for opt in options:
                if opt.strip():
                    poll_option = PollOption(poll_id=poll.id, option_text=opt.strip())
                    db.session.add(poll_option)
            db.session.commit()
            return redirect(url_for('community'))
    return render_template('create_poll.html')

@app.route('/poll/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if request.method == 'POST':
        option_id = request.form.get('option')
        option = PollOption.query.filter_by(id=option_id, poll_id=poll.id).first()
        if option:
            # Optionnel : vérifier qu'un utilisateur ne vote qu'une seule fois
            option.votes += 1
            vote = PollVote(poll_id=poll.id, user_id=current_user.id, poll_option_id=option.id)
            db.session.add(vote)
            db.session.commit()
        return redirect(url_for('poll', poll_id=poll.id))
    total_votes = sum(opt.votes for opt in poll.options)
    return render_template('poll.html', poll=poll, total_votes=total_votes)

@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
@admin_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        question_text = request.form.get('question')
        choices = request.form.getlist('choice')
        correct_choice = request.form.get('correct_choice')
        if title and question_text and choices and correct_choice:
            quiz = Quiz(title=title, description=description)
            db.session.add(quiz)
            db.session.flush()  # pour obtenir quiz.id
            question = Question(quiz_id=quiz.id, text=question_text)
            db.session.add(question)
            db.session.flush()  # pour obtenir question.id
            for idx, choice_text in enumerate(choices):
                is_right = (str(idx) == correct_choice)
                choice = Choice(question_id=question.id, text=choice_text, is_right=is_right)
                db.session.add(choice)
            db.session.commit()
            return redirect(url_for('community'))
    return render_template('create_quiz.html')


@app.route('/community_poll_vote/<int:poll_id>', methods=['POST'])
@login_required
def community_poll_vote(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    try:
        option_id = int(request.form.get('option'))
    except (ValueError, TypeError):
        return redirect(url_for('community'))
    option = PollOption.query.filter_by(id=option_id, poll_id=poll.id).first()
    if option:
        # Empêche un utilisateur de voter plusieurs fois
        existing_vote = PollVote.query.filter_by(poll_id=poll.id, user_id=current_user.id).first()
        if not existing_vote:
            option.votes += 1
            vote = PollVote(poll_id=poll.id, user_id=current_user.id, poll_option_id=option.id)
            db.session.add(vote)
            db.session.commit()
    return redirect(url_for('community'))

@app.route('/etage_0')
def etage_0():
    return render_template('etage_0.html')

@app.route('/etage_1')
def etage_1():
    return render_template('etage_1.html')

@app.route('/etage_2')
def etage_2():
    return render_template('etage_2.html')

@app.route('/admin/jardin/<int:jardin_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_jardin(jardin_id):
    jardin = Jardin.query.get_or_404(jardin_id)
    # Pour alimenter le menu déroulant dans le template.
    legumes = Legume.query.all()
    if request.method == 'POST':
        for slot in jardin.slots:
            # Récupère l'id du légume choisi dans le formulaire (chaîne vide si aucun légume)
            legume_id = request.form.get(f'slot_{slot.id}')
            if legume_id:
                try:
                    slot.legume_id = int(legume_id)
                except ValueError:
                    slot.legume_id = None
            else:
                slot.legume_id = None
        db.session.commit()
        return redirect(url_for('jardin_detail', jardin_id=jardin.id))
    
    return render_template('admin_edit_jardin.html', jardin=jardin, legumes=legumes)
if __name__ == '__main__':
    app.run(debug=True)