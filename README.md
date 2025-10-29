# Projet de migration de données médicales vers MongoDB via Docker

Ce projet contient un processus automatisé pour migrer des données médicales d'un fichier CSV vers une base de données MongoDB, le tout entièrement conteneurisé à l'aide de Docker et Docker Compose.

## Prérequis

* [Docker]
* [Docker Compose]

## Comment lancer la migration

L'ensemble du processus de migration est automatisé et peut être lancé avec une seule commande depuis la racine de ce projet.

```bash
docker-compose up -d --build
```

## Déroulement du processus de migration

Lors du lancement de la commande docker-compose up, la séquence d’événements suivante se produit :

1.  **Orchestration** : `docker-compose` lit le fichier `docker-compose.yml` et connecte les services au réseau.

2.  **Démarrage de la base de données** : Le service `mongodb` est démarré. Une base de données MongoDB 5.0 est initialisée et un volume nommé `mongo-data` est créé pour assurer la persistance des données.

3.  **Démarrage du service de migration** : Le service `migration_process` est démarré. Il exécute la commande suivante, qui enchaîne plusieurs scripts Python :

    *   **`clean_csv.py`** : Ce script lit le fichier source `healthcare_dataset.csv`, effectue des opérations de nettoyage et sauvegarde le résultat dans `healthcare_dataset_cleaned.csv`.

    *   **`migration.py`** : Le cœur du processus. Ce script se connecte à la base de données, vide la collection `patients` pour garantir une migration propre, lit le fichier `healthcare_dataset_cleaned.csv`, et insère les données dans la collection.

    *   **`test_integrity.py`** : Une fois la migration terminée, ce script exécute automatiquement une série de tests pour valider l'intégrité des données dans MongoDB.

4.  **Fin du processus** : Une fois tous les scripts exécutés avec succès, le conteneur `migration_process` s'arrête.


## Connexion avec MongoDB Compass

Pour visualiser les données dans MongoDB Compass :

- **Chaîne de connexion** :
  ```
  mongodb://root:password@localhost:27017/?authSource=admin
  ```
- **Configuration avancée** :
  - Allez dans l'onglet `More Options`.
  - Vérifiez que le paramètre **`TLS/SSL`** est bien sur **`None`**.

**Dépannage :**
Si la connexion échoue, assurez-vous qu'aucun autre service (comme une instance locale de MongoDB) n'utilise le port `27017` sur votre machine.


## Comment vérifier le résultat

*   **Consulter les logs** : Pour voir le détail de chaque étape du processus, utilisez la commande :
    ```bash
    docker-compose logs migration_process
    ```

*   **Inspecter la base de données (ligne de commande)** : Pour connecter directement à la base de données et voir un exemple de document inséré, utilisez la commande suivante :
    ```bash
    docker exec -it mongodb mongosh -u root -p password --eval "use healthcare; db.patients.findOne();"
    ```

## Comment nettoyer l'environnement

Pour arrêter et supprimer tous les conteneurs, réseaux et volumes créés par `docker-compose`, exécutez la commande :

```bash
docker-compose down -v
```

*   L'option `-v` est importante car elle supprime également le volume `mongo-data`, en assurant de repartir de zéro lors de la prochaine exécution.