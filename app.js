// Dans app.js ou server.js (fichier principal de l'application)
const express = require('express');
const session = require('express-session');
const mysql = require('mysql2/promise');
const path = require('path');

const app = express();

// Configuration de la session
app.use(session({
  secret: 'votre_clé_secrète',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // Mettre à true en production avec HTTPS
}));

// Configuration du moteur de template EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware pour servir les fichiers statiques
app.use(express.static(path.join(__dirname, 'public')));

// Configuration de la base de données
const dbConfig = {
  host: 'localhost',
  user: 'username',
  password: 'password',
  database: 'mydb'
};

// Middleware pour vérifier si l'utilisateur est connecté
const isAuthenticated = (req, res, next) => {
  if (req.session.userId) {
    next();
  } else {
    res.redirect('/login');
  }
};

// Route pour la page de profil
app.get('/profile', isAuthenticated, async (req, res) => {
  try {
    // Créer une connexion à la base de données
    const connection = await mysql.createConnection(dbConfig);
    
    // Récupérer les informations de l'utilisateur
    const [userRows] = await connection.execute(
      'SELECT nom, prenom, email, statut, photo_profil FROM utilisateurs WHERE id = ?',
      [req.session.userId]
    );
    
    // Récupérer les badges de l'utilisateur
    const [badgeRows] = await connection.execute(
      `SELECT b.image_url, b.nom 
       FROM badges b
       JOIN utilisateur_badges ub ON b.id = ub.badge_id
       WHERE ub.utilisateur_id = ?`,
      [req.session.userId]
    );
    
    // Fermer la connexion
    await connection.end();
    
    // Si l'utilisateur n'est pas trouvé, rediriger vers la page de connexion
    if (userRows.length === 0) {
      req.session.destroy();
      return res.redirect('/login');
    }
    
    // Rendre la vue avec les données de l'utilisateur
    res.render('profile', {
      user: userRows[0],
      badges: badgeRows
    });
    
  } catch (error) {
    console.error('Erreur lors de la récupération des données :', error);
    res.status(500).send('Erreur serveur');
  }
});

// Route pour se déconnecter
app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/login');
});

// Démarrer le serveur
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
});