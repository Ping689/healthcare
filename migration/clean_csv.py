import csv
import re
import os
from decimal import Decimal, ROUND_HALF_UP

def clean_csv_file(input_file_path, output_file_path):
    """
    Nettoie un fichier CSV en standardisant les champs de texte, en arrondissant les montants de facturation,
    et en supprimant les lignes en double.

    :param input_file_path: Chemin vers le fichier CSV source.
    :param output_file_path: Chemin pour écrire le fichier CSV nettoyé.
    """
    print(f"Démarrage du processus de nettoyage pour {input_file_path}...")

    cleaned_data = []
    seen = set()

    try:
        with open(input_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                try:
                    # Nettoyer les champs de texte
                    # Nettoyer le champ Nom en supprimant les préfixes
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

                    # Formater le montant de la facturation
                    billing_amount = Decimal(row['Billing Amount']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    row['Billing Amount'] = str(billing_amount)

                except (ValueError, TypeError) as e:
                    print(f"Ligne ignorée en raison d'une erreur de conversion de données : {row} - Erreur : {e}")
                    continue

                # Créer un tuple des éléments du dictionnaire pour le rendre hachable
                row_tuple = tuple(row.items())
                if row_tuple not in seen:
                    seen.add(row_tuple)
                    cleaned_data.append(row)

        print(f"Lecture de {csv_reader.line_num - 1} lignes et trouvé {len(cleaned_data)} lignes uniques après nettoyage.")

        # Écrire dans un nouveau CSV
        if cleaned_data:
            with open(output_file_path, mode='w', encoding='utf-8', newline='') as csv_output_file:
                # Utiliser les noms de champs de la première ligne nettoyée
                fieldnames = cleaned_data[0].keys()
                writer = csv.DictWriter(csv_output_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(cleaned_data)
            print(f"Fichier nettoyé créé avec succès : {output_file_path}")
        else:
            print("Aucune donnée à écrire après le nettoyage.")

    except FileNotFoundError:
        print(f"Erreur : Le fichier {input_file_path} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite lors du processus de nettoyage : {e}")

if __name__ == "__main__":
    # Obtenir la configuration à partir des variables d'environnement
    INPUT_CSV_FILE = os.environ.get('INPUT_CSV_FILE', 'healthcare_dataset.csv')
    OUTPUT_CSV_FILE = os.environ.get('OUTPUT_CSV_FILE', 'healthcare_dataset_cleaned.csv')

    # Exécuter le processus de nettoyage
    clean_csv_file(INPUT_CSV_FILE, OUTPUT_CSV_FILE)