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

   ### Sous macOS et Linux

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   ### Sous Windows

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
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

   - Ouvrez le fichier `.env` et modifiez la valeur de `SECRET_KEY` pour qu'elle soit suffisamment complexe. Modifier la valeur `PLANTNET_API_KEY` avec votre clé API de Pl@ntNet API sur [ce lien.](https://my.plantnet.org)

5. **Configurer la base de données**

   La base de données SQLite est configurée avec Flask-SQLAlchemy.
   Elle sera automatiquement créée dans le répertoire `instance` lors du lancement de l'application.

## Alimentation de la base de données

L'application fournit plusieurs scripts Python permettant d'alimenter la base de données avec des données initiales ou de test. Pour les utiliser, suivez les étapes ci-dessous :

1. Activez votre environnement virtuel.
2. Exécutez le script souhaité. Par exemple pour alimenter les quiz :

   ```bash
   python populate_db.py
   ```

## Fonctionnalités

- Identification des plantes via l'API [Pl@ntNet](https://my.plantnet.org)
- Gestion de la base de données SQLite avec Flask-SQLAlchemy
- Système de vote pour les jardins stocké dans la BDD
- Système d'administration pour poster des messages dans l'onglet communauté, modifier des jardins, créer des quiz et des sondages
- Information météo en direct grâce à l'API [Open-Meteo](https://open-meteo.com/)
