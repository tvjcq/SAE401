# language: python
from app import db, User, Jardin, Legume, SlotJardin, app

with app.app_context():
    # Retrieve an existing user to be the owner of the gardens.
    owner = User.query.first()
    if not owner:
        # Create a dummy owner if none exists.
        owner = User(
            email="owner@example.com",
            password="dummy",  # In production, use a proper hashed password
            last_name="Owner",
            first_name="Dummy",
            status="Étudiant"
        )
        db.session.add(owner)
        db.session.commit()

    
    
    # Data for gardens with associated slots and vegetables.
    gardens_data = [
        {
            "nom": "Jardin de Provence",
            "type": "exterieur",
            "slots": [
                {
                    "position": "A1",
                    "legume": {"nom": "Tomate", "description": "Juteuse et sucrée"}
                },
                {
                    "position": "A2",
                    "legume": {"nom": "Carotte", "description": "Croquante et riche en bêta-carotène"}
                },
            ]
        },
        {
            "nom": "Potager Urbain",
            "type": "interieur",
            "slots": [
                {
                    "position": "B1",
                    "legume": {"nom": "Laitue", "description": "Fraîche et croquante"}
                },
                {
                    "position": "B2",
                    "legume": None  
                },
            ]
        }
    ]

    for garden_info in gardens_data:
        jardin = Jardin(nom=garden_info["nom"], type=garden_info["type"], proprietaire_id=owner.id)
        db.session.add(jardin)
        db.session.flush()  # Pour obtenir l'id du jardin

        for slot_info in garden_info["slots"]:
            legume_data = slot_info.get("legume")
            if legume_data:
                legume = Legume(nom=legume_data["nom"], description=legume_data["description"])
                db.session.add(legume)
                db.session.flush()  # pour obtenir l'id
            else:
                legume = None  # slot vide
            slot = SlotJardin(jardin_id=jardin.id, legume_id=legume.id if legume else None, position=slot_info["position"])
            db.session.add(slot)
    
    db.session.commit()
    print("Garden data populated!")