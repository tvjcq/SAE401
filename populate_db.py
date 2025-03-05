from app import db, Quiz, Question, Choice, app

# Updated quizzes_data for gardening-related quizzes
quizzes_data = [
    {
        "title": "Secrets des Fleurs",
        "description": "Découvrez comment cultiver et entretenir vos fleurs favorites.",
        "questions": [
            {
                "text": "Quelle saison est la meilleure pour planter des tulipes ?",
                "choices": [
                    {"text": "L'automne", "is_right": True},
                    {"text": "Le printemps", "is_right": False},
                    {"text": "L'été", "is_right": False}
                ],
            },
            {
                "text": "Quel sol favorise la croissance des roses ?",
                "choices": [
                    {"text": "Un sol riche et bien drainé", "is_right": True},
                    {"text": "Un sol sableux", "is_right": False},
                    {"text": "Un sol argileux sans amendement", "is_right": False}
                ],
            },
            {
                "text": "Quelle est l'importance de la taille des fleurs fanées ?",
                "choices": [
                    {"text": "Elle stimule la floraison", "is_right": True},
                    {"text": "Elle empêche la plante de se développer", "is_right": False},
                    {"text": "Aucun effet", "is_right": False}
                ],
            },
            {
                "text": "Comment prévenir les maladies fongiques sur les fleurs ?",
                "choices": [
                    {"text": "En assurant une bonne aération", "is_right": True},
                    {"text": "En arrosant en soirée", "is_right": False},
                    {"text": "En ajoutant plus d'engrais", "is_right": False}
                ],
            },
            {
                "text": "Quel est le rôle du paillage dans l'entretien des fleurs ?",
                "choices": [
                    {"text": "Il conserve l'humidité et réduit les mauvaises herbes", "is_right": True},
                    {"text": "Il empêche la lumière de pénétrer", "is_right": False},
                    {"text": "Il enrichit immédiatement le sol en nutriments", "is_right": False}
                ],
            }
        ],
    },
    {
        "title": "Jardinage Écologique",
        "description": "Apprenez des techniques écologiques pour un jardin respectueux de la nature.",
        "questions": [
            {
                "text": "Quelle méthode est recommandée pour lutter contre les parasites sans pesticides ?",
                "choices": [
                    {"text": "La lutte biologique", "is_right": True},
                    {"text": "L'utilisation d'engrais chimiques", "is_right": False},
                    {"text": "L'irrigation excessive", "is_right": False}
                ],
            },
            {
                "text": "Pourquoi favoriser le compost dans le jardinage écologique ?",
                "choices": [
                    {"text": "Il améliore la fertilité du sol naturellement", "is_right": True},
                    {"text": "Il augmente la teneur en sels", "is_right": False},
                    {"text": "Il attire les nuisibles", "is_right": False}
                ],
            },
            {
                "text": "Quelle plante attire les insectes bénéfiques dans le jardin ?",
                "choices": [
                    {"text": "La lavande", "is_right": True},
                    {"text": "Le châtaignier", "is_right": False},
                    {"text": "Le cactus", "is_right": False}
                ],
            },
            {
                "text": "Comment économiser l'eau en jardinage écologique ?",
                "choices": [
                    {"text": "En utilisant le paillage et une irrigation au goutte-à-goutte", "is_right": True},
                    {"text": "En arrosant en plein soleil", "is_right": False},
                    {"text": "En augmentant la fréquence d'arrosage", "is_right": False}
                ],
            },
            {
                "text": "Quel est l'avantage de la rotation des cultures ?",
                "choices": [
                    {"text": "Elle permet d'éviter l'épuisement des nutriments du sol", "is_right": True},
                    {"text": "Elle augmente la quantité de mauvaises herbes", "is_right": False},
                    {"text": "Elle n'a aucun impact sur le sol", "is_right": False}
                ],
            }
        ],
    },
    {
        "title": "Techniques de Taille",
        "description": "Maîtrisez l'art de la taille pour des arbustes et arbres en pleine santé.",
        "questions": [
            {
                "text": "Quelle est la principale raison de tailler un arbre fruitier ?",
                "choices": [
                    {"text": "Favoriser une meilleure production de fruits", "is_right": True},
                    {"text": "Pour le décourager de croître", "is_right": False},
                    {"text": "Aucune raison spécifique", "is_right": False}
                ],
            },
            {
                "text": "À quel moment de l'année est-il conseillé de tailler la plupart des arbustes ?",
                "choices": [
                    {"text": "En hiver", "is_right": True},
                    {"text": "Au printemps", "is_right": False},
                    {"text": "En été", "is_right": False}
                ],
            },
            {
                "text": "Quel outil est indispensable pour une taille précise ?",
                "choices": [
                    {"text": "Un sécateur bien affûté", "is_right": True},
                    {"text": "Une hache", "is_right": False},
                    {"text": "Un marteau", "is_right": False}
                ],
            },
            {
                "text": "Pourquoi est-il important de désinfecter ses outils de taille ?",
                "choices": [
                    {"text": "Pour prévenir la propagation de maladies", "is_right": True},
                    {"text": "Pour les rendre plus brillants", "is_right": False},
                    {"text": "Cela n'a pas d'importance", "is_right": False}
                ],
            },
            {
                "text": "Quel est le risque d'une taille trop sévère ?",
                "choices": [
                    {"text": "La fragilisation de l'arbre", "is_right": True},
                    {"text": "Une floraison plus abondante", "is_right": False},
                    {"text": "Aucun risque", "is_right": False}
                ],
            }
        ],
    }
]

with app.app_context():
    for quiz_info in quizzes_data:
        quiz = Quiz(title=quiz_info["title"], description=quiz_info["description"])
        db.session.add(quiz)
        db.session.flush()  # to get quiz id for foreign key
        
        for q_info in quiz_info["questions"]:
            question = Question(quiz_id=quiz.id, text=q_info["text"])
            db.session.add(question)
            db.session.flush()  # to get question id
            
            for choice_info in q_info["choices"]:
                choice = Choice(question_id=question.id, text=choice_info["text"], is_right=choice_info["is_right"])
                db.session.add(choice)
    
    db.session.commit()
    print("Database populated!")