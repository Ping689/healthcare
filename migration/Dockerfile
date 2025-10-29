# Utiliser une image Python officielle et légère
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances et les installer
# Copier ce fichier en premier permet de profiter du cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les scripts python et le fichier de données source
COPY clean_csv.py .
COPY migration.py .
COPY test_integrity.py .
COPY healthcare_dataset.csv .

# Définir la commande à exécuter lorsque le conteneur démarre
CMD ["python", "migration.py"]