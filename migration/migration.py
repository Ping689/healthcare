import csv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime
import os

def migrate_csv_to_mongodb(csv_file_path, db_name, collection_name, mongo_uri):
    """
    Migre les données d'un fichier CSV nettoyé vers une collection MongoDB.

    :param csv_file_path: Chemin vers le fichier CSV nettoyé.
    :param db_name: Nom de la base de données MongoDB.
    :param collection_name: Nom de la collection MongoDB.
    :param mongo_uri: L'URI de connexion MongoDB.
    """
    print("Démarrage du processus de migration depuis un fichier nettoyé...")

    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("Connecté avec succès à MongoDB.")
    except ConnectionFailure as e:
        print(f"Impossible de se connecter à MongoDB : {e}")
        return

    db = client[db_name]
    collection = db[collection_name]

    print(f"Nettoyage des données existantes de la collection : {collection_name}...")
    collection.delete_many({})

    print(f"Lecture des données depuis {csv_file_path} et insertion dans MongoDB...")
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            data_to_insert = []
            for row in csv_reader:
                try:
                    # Conversion des types de données pour MongoDB
                    row['Age'] = int(row['Age'])
                    row['Billing Amount'] = Decimal128(Decimal(row['Billing Amount']))
                    row['Date of Admission'] = datetime.strptime(row['Date of Admission'], '%Y-%m-%d')
                    row['Discharge Date'] = datetime.strptime(row['Discharge Date'], '%Y-%m-%d')
                    
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Ligne ignorée en raison d'une erreur de conversion ou de clé manquante : {row} - Erreur : {e}")
                    continue
                data_to_insert.append(row)
   
            if data_to_insert:
                collection.insert_many(data_to_insert)
                print(f"{len(data_to_insert)} documents insérés avec succès dans la collection.")
            else:
                print("Aucune donnée à insérer.")

    except FileNotFoundError:
        print(f"Erreur : Le fichier {csv_file_path} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la migration : {e}")
    finally: 
        client.close()
        print("Connexion MongoDB fermée.")

if __name__ == "__main__":
    CSV_FILE = os.getenv('OUTPUT_CSV_FILE', 'healthcare_dataset_cleaned.csv')
    DB_NAME = os.getenv('DB_NAME', 'healthcare')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'patients')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    migrate_csv_to_mongodb(CSV_FILE, DB_NAME, COLLECTION_NAME, MONGO_URI)