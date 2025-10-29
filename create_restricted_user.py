import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def create_test_user():
    """
    Se connecte à MongoDB avec les identifiants administrateur et crée un 'test_user'
    sans aucune permission sur la base de données 'healthcare'.
    """
    # On se connecte à la base de données 'admin' pour créer des utilisateurs.
    # L'URI MONGO devrait contenir les identifiants de l'administrateur.
    mongo_uri = os.getenv("MONGO_URI", "mongodb://root:password@localhost:27017/admin")
    
    print("Connexion à MongoDB pour créer un utilisateur de test...")
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("Connecté avec succès à MongoDB en tant qu'administrateur.")
    except ConnectionFailure as e:
        print(f"Impossible de se connecter à MongoDB en tant qu'administrateur : {e}")
        return

    db = client.healthcare
    
    # L'utilisateur sera créé dans le contexte de la base de données 'healthcare',
    # mais aucun rôle ne lui sera attribué.
    try:
        # Supprimer l'utilisateur s'il existe déjà, pour garantir un état propre.
        db.command("dropUser", "test_user")
        print("Utilisateur 'test_user' existant supprimé.")
    except Exception:
        # L'utilisateur n'existe probably pas, ce qui est normal.
        pass

    # Créer l'utilisateur avec un tableau de rôles vide pour cette base de données.
    db.command("createUser", "test_user", pwd="test_password", roles=[])
    print("Utilisateur 'test_user' créé avec succès sans aucun rôle sur la base de données 'healthcare'.")
    
    client.close()
    print("Connexion MongoDB fermée.")

if __name__ == "__main__":
    create_test_user()
