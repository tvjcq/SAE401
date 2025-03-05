# SAE401 Plant It Flask App

Application construite avec FLask avec une base de donnée SQLite.

## Prérequis

- Python 3.9 ou supérieur
- pip

## Installation

1. **Cloner le dépôt**

   Clonez ce dépot sur votre machine

2. **Créer un environnement virtuel**

   Dans le répertoire du projet, créez et activez votre environnement virtuel :

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer les dépendances**
   Installez les paquets requis depuis le fichier `requirements.txt` :

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**

   - Copiez le fichier d'exemple et renommez-le en `.env` :

     ```bash
     cp .env.example .env
     ```

   - Ouvrez le fichier `.env` et modifiez la valeur de `SECRET_KEY` pour qu'elle soit suffisamment complexe

5. **Configurer les variables d'environnement**

   La base de données SQLite est configurée avec Flask-SQLAlchemy.
   Elle sera automatiquement créée dans le répertoire `instance` lors du lancement de l'application.
