import os
from pymongo import MongoClient

def test_data_integrity(db_name, collection_name, mongo_uri=None):
    """
    Effectue des tests d'intégrité des données sur une collection MongoDB.

    :param db_name: Nom de la base de données MongoDB.
    :param collection_name: Nom de la collection MongoDB.
    :param mongo_uri: L'URI de connexion MongoDB.
    """
    if mongo_uri is None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    print("Démarrage des tests d'intégrité des données...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # 1. Vérifier si la collection contient des documents
    document_count = collection.count_documents({})
    print(f"Test 1 : Nombre de documents. Trouvé {document_count} documents.")
    assert document_count > 0, "Échec du test 1 : Aucun document trouvé dans la collection."
    print("Test 1 réussi : La collection n'est pas vide.")

    # 2. Vérifier que les champs attendus sont présents
    print("\nTest 2 : Présence des champs.")
    expected_fields = ['Name', 'Age', 'Gender', 'Blood Type', 'Medical Condition', 'Date of Admission', 'Doctor', 'Hospital', 'Insurance Provider', 'Billing Amount', 'Room Number', 'Admission Type', 'Discharge Date', 'Medication', 'Test Results']
    sample_document = collection.find_one()
    missing_fields = [field for field in expected_fields if field not in sample_document]
    assert not missing_fields, f"Échec du test 2 : Champs manquants : {missing_fields}"
    print("Test 2 réussi : Tous les champs attendus sont présents dans un document échantillon.")

    # 3. Vérifier les valeurs manquantes dans les champs clés
    print("\nTest 3 : Vérifier les valeurs nulles ou vides dans le champ 'Name'.")
    null_name_count = collection.count_documents({"Name": {"$in": [None, ""]}})
    assert null_name_count == 0, f"Échec du test 3 : Trouvé {null_name_count} documents avec des noms nuls ou vides."
    print("Test 3 réussi : Aucun document avec des noms nuls ou vides.")

    # 4. Vérifier les doublons
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
