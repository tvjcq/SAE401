import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('baselocale.db')
c = conn.cursor()

# Création de la table profile
c.execute("""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    statut TEXT NOT NULL
)
""")

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