import os
import csv
from pymongo import MongoClient

def get_csv_headers(file_path):
    """Lit la première ligne d'un fichier CSV et retourne les en-têtes."""
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            return headers
    except FileNotFoundError:
        print(f"Erreur : Le fichier CSV {file_path} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture des en-têtes CSV : {e}")
        return None

def test_data_integrity(db_name, collection_name, mongo_uri=None):
    """
    Effectue des tests d'intégrité des données sur une collection MongoDB.

    :param db_name: Nom de la base de données MongoDB.
    :param collection_name: Nom de la collection MongoDB.
    :param mongo_uri: L'URI de connexion MongoDB.
    """
    if mongo_uri is None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    
    cleaned_csv_path = os.getenv('OUTPUT_CSV_FILE', 'healthcare_dataset_cleaned.csv')

    print("Démarrage des tests d'intégrité des données...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    document_count = collection.count_documents({})
    print(f"Test 1 : Nombre de documents. Trouvé {document_count} documents.")
    assert document_count > 0, "Échec du test 1 : Aucun document trouvé dans la collection."
    print("Test 1 réussi : La collection n'est pas vide.")

    expected_fields = get_csv_headers(cleaned_csv_path)
    if not expected_fields:
        print("Impossible de procéder aux tests de champs et de doublons sans les en-têtes CSV.")
        client.close()
        return

    print("\nTest 2 : Présence des champs.")
    sample_document = collection.find_one()
    missing_fields = [field for field in expected_fields if field not in sample_document]
    assert not missing_fields, f"Échec du test 2 : Champs manquants : {missing_fields}"
    print("Test 2 réussi : Tous les champs attendus sont présents dans un document échantillon.")

    print("\nTest 3 : Vérifier les valeurs nulles ou vides dans le champ 'Name'.")
    null_name_count = collection.count_documents({"Name": {"$in": [None, ""]}})
    assert null_name_count == 0, f"Échec du test 3 : Trouvé {null_name_count} documents avec des noms nuls ou vides."
    print("Test 3 réussi : Aucun document avec des noms nuls ou vides.")

    print("\nTest 4 : Vérifier les documents en double.")
    pipeline = [
        {
            "$group": {
                "_id": {key: f"${key}" for key in expected_fields}, 
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "count": {"$gt": 1}
            }
        }
    ]
    duplicates = list(collection.aggregate(pipeline))
    assert len(duplicates) == 0, f"Échec du test 4 : Trouvé {len(duplicates)} documents en double."
    print("Test 4 réussi : Aucun document en double trouvé.")

    print("\nTous les tests d'intégrité des données ont réussi !")
    client.close()

if __name__ == "__main__":
    DB_NAME = 'healthcare'
    COLLECTION_NAME = 'patients'
    test_data_integrity(DB_NAME, COLLECTION_NAME)
