import csv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.decimal128 import Decimal128
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import re
import os

def migrate_csv_to_mongodb(csv_file_path, db_name, collection_name, mongo_uri):
    """
    Migre les données d'un fichier CSV vers une collection MongoDB.

    :param csv_file_path: Chemin vers le fichier CSV.
    :param db_name: Nom de la base de données MongoDB.
    :param collection_name: Nom de la collection MongoDB.
    :param mongo_uri: L'URI de connexion MongoDB.
    """
    print("Démarrage du processus de migration...")

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
                    name = row['Name']
                    name = re.sub(r'^(Mr\.|Mrs\.|Dr\.|Miss)\s*', '', name, flags=re.IGNORECASE)
                    row['Name'] = name.strip().title()
                    row['Gender'] = row['Gender'].title()
                    row['Medical Condition'] = row['Medical Condition'].title()
                    row['Admission Type'] = row['Admission Type'].title()
                    row['Medication'] = row['Medication'].title()
                    row['Test Results'] = row['Test Results'].title()
                    row['Doctor'] = row['Doctor'].title()
                    row['Hospital'] = row['Hospital'].title()
                    row['Insurance Provider'] = row['Insurance Provider'].title()

                    row['Age'] = int(row['Age'])
                    billing_amount_decimal = Decimal(row['Billing Amount']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    row['Billing Amount'] = Decimal128(billing_amount_decimal)
                    
                    row['Date of Admission'] = datetime.strptime(row['Date of Admission'], '%Y-%m-%d')
                    row['Discharge Date'] = datetime.strptime(row['Discharge Date'], '%Y-%m-%d')
                    
                except (ValueError, TypeError) as e:
                    print(f"Ligne ignorée en raison d'une erreur de conversion de données : {row} - Erreur : {e}")
                    continue
                data_to_insert.append(row)

           
            unique_data = []
            seen = set()
            for row in data_to_insert:
                hashable_row = {}
                for k, v in row.items():
                    if isinstance(v, Decimal128):
                        hashable_row[k] = str(v) 
                    else:
                        hashable_row[k] = v
                
                row_tuple = tuple(sorted(hashable_row.items())) 
                
                if row_tuple not in seen:
                    seen.add(row_tuple)
                    unique_data.append(row)
            
            print(f"{len(data_to_insert) - len(unique_data)} lignes en double supprimées.")

           
            if unique_data:
                collection.insert_many(unique_data)
                print(f"{len(unique_data)} documents uniques insérés avec succès dans la collection.")
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
    CSV_FILE = os.getenv('INPUT_CSV_FILE', 'healthcare_dataset.csv')
    DB_NAME = os.getenv('DB_NAME', 'healthcare')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'patients')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    migrate_csv_to_mongodb(CSV_FILE, DB_NAME, COLLECTION_NAME, MONGO_URI)
