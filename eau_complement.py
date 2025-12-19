import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, regexp_replace, date_trunc, sum, mean

# --- CONFIGURATION JAVA ---
# On garde cette configuration indispensable pour votre environnement
os.environ['PYSPARK_SUBMIT_ARGS'] = (
    "--driver-java-options '--add-opens=java.base/java.lang=ALL-UNNAMED "
    "--add-opens=java.base/java.util=ALL-UNNAMED "
    "--add-opens=java.base/java.nio=ALL-UNNAMED' pyspark-shell"
)

# --- CONFIGURATION DES CHEMINS ---
# Nom du dossier cible
nom_dossier = "CSVs"

# On construit les chemins complets compatibles Windows/Linux
# Fichier d'entrée : CSVs/eau_converted.csv
chemin_entree = os.path.join(nom_dossier, "eau_converted.csv")

# Fichiers de sortie
chemin_sortie_horaire = os.path.join(nom_dossier, "eau_horaire.csv")
chemin_sortie_moyenne = os.path.join(nom_dossier, "eau_horaire_moyenne.csv")

# Petit contrôle de sécurité pour vérifier que le dossier existe
if not os.path.exists(nom_dossier):
    print(f"ATTENTION : Le dossier '{nom_dossier}' n'existe pas dans le répertoire courant.")
    print("Veuillez créer le dossier 'CSVs' et y placer votre fichier 'eau_converted.csv'.")
    sys.exit(1)

# --- DEBUT DU TRAITEMENT SPARK ---
spark = SparkSession.builder \
    .appName("AnalysePluie") \
    .getOrCreate()

print(f"Lecture du fichier : {chemin_entree}")

try:
    # 1. Chargement
    df = spark.read \
        .option("header", "true") \
        .option("delimiter", ";") \
        .csv(chemin_entree)

    # 2. Nettoyage
    print("Nettoyage et conversion des données...")
    df_clean = df \
        .withColumn("horodate", to_timestamp(col("horodate"))) \
        .withColumn("pluie_mm", regexp_replace(col("pluie_mm"), ",", ".").cast("double")) \
        .withColumn("date_heure", date_trunc("hour", col("horodate")))

    # 3. Calcul : Somme par identifiant
    print("Calcul des sommes par identifiant...")
    df_horaire_spark = df_clean.groupBy("identifiant", "date_heure") \
        .agg(sum("pluie_mm").alias("pluie_somme")) \
        .orderBy("identifiant", "date_heure")

    # 4. Calcul : Moyenne globale
    print("Calcul de la moyenne globale...")
    df_moyenne_spark = df_clean.groupBy("date_heure") \
        .agg(mean("pluie_mm").alias("pluie_moyenne")) \
        .orderBy("date_heure")

    # 5. Sauvegarde en CSV unique (via Pandas)
    print(f"Sauvegarde dans le dossier '{nom_dossier}'...")

    # Conversion en Pandas et écriture dans le dossier CSVs
    df_horaire_spark.toPandas().to_csv(chemin_sortie_horaire, sep=";", decimal=",", index=False)
    df_moyenne_spark.toPandas().to_csv(chemin_sortie_moyenne, sep=";", decimal=",", index=False)

    print("Traitement terminé avec succès !")
    print(f"Fichiers générés :\n - {chemin_sortie_horaire}\n - {chemin_sortie_moyenne}")

except Exception as e:
    print("Une erreur est survenue lors du traitement :")
    print(e)

finally:
    spark.stop()