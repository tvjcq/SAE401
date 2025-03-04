import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('baselocale.db')
c = conn.cursor()

# Création de la table profile avec la colonne password
c.execute("""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT,
    statut TEXT NOT NULL
)
""")

# Vérifier si la colonne password existe, sinon l'ajouter
c.execute("PRAGMA table_info(profile)")
columns = [column[1] for column in c.fetchall()]
if 'password' not in columns:
    c.execute("ALTER TABLE profile ADD COLUMN password TEXT")

# Mettre à jour les enregistrements existants pour définir une valeur par défaut pour la colonne password
c.execute("UPDATE profile SET password = 'default_password' WHERE password IS NULL")

# Insertion de données dans la table profile
c.execute("""
INSERT INTO profile (nom, prenom, email, password, statut) VALUES
    ('Doe', 'John', 'john.doe@example.com', 'hashed_password', 'Membre'),
    ('Smith', 'Jane', 'jane.smith@example.com', 'hashed_password', 'Admin')
""")

# Validation des changements
conn.commit()

# Sélection et affichage des données de la table profile
c.execute("SELECT * FROM profile")
rows = c.fetchall()

for row in rows:
    print('{0} : {1} - {2} - {3} - {4} - {5}'.format(row[0], row[1], row[2], row[3], row[4], row[5]))

# Fermeture de la connexion
conn.close()