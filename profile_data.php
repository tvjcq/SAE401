<!-- filepath: /c:/Users/Utilisateur/Documents/MMI/MMI 2/S4/SAÉ/saé 401 Dev web/SAE401/profile_data.php -->
<?php
// Démarrer ou reprendre la session
session_start();

// Vérifier si l'utilisateur est connecté
if (!isset($_SESSION['user_id'])) {
  // Si non connecté, rediriger vers la page de connexion
  header('Location: login.php');
  exit;
}

// Se connecter à la base de données
$servername = "localhost";
$username = "username";
$password = "password";
$dbname = "mydb";

try {
  $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
  $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  
  // Préparer et exécuter la requête pour récupérer les informations de l'utilisateur
  $stmt = $conn->prepare("SELECT nom, prenom, email, statut, photo_profil FROM utilisateurs WHERE id = :id");
  $stmt->bindParam(':id', $_SESSION['user_id'], PDO::PARAM_INT);
  $stmt->execute();
  
  // Récupérer les données
  $user = $stmt->fetch(PDO::FETCH_ASSOC);
  
  // Récupérer les badges de l'utilisateur
  $stmt = $conn->prepare("
    SELECT b.image_url, b.nom 
    FROM badges b
    JOIN utilisateur_badges ub ON b.id = ub.badge_id
    WHERE ub.utilisateur_id = :id
  ");
  $stmt->bindParam(':id', $_SESSION['user_id'], PDO::PARAM_INT);
  $stmt->execute();
  
  $badges = $stmt->fetchAll(PDO::FETCH_ASSOC);
  
} catch(PDOException $e) {
  echo "Erreur de connexion: " . htmlspecialchars($e->getMessage());
  exit;
}
?>