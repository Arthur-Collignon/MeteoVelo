import pandas as pd

# Configuration des fichiers
fichier_entree = './CSVs/eau_converted.csv'
fichier_sortie = './CSVs/eau_processed.csv'

# 1. Chargement des données
# On précise le séparateur ';' utilisé dans votre fichier
df = pd.read_csv(fichier_entree, sep=';')

# 2. Nettoyage et conversion des types
# Conversion de la colonne 'horodate' en format date/heure
df['horodate'] = pd.to_datetime(df['horodate'])

# Conversion de la colonne 'pluie_mm' en nombres (remplacement de la virgule par un point)
# Cette étape gère le format français des nombres (ex: "0,1" -> 0.1)
if df['pluie_mm'].dtype == 'object':
    df['pluie_mm'] = df['pluie_mm'].astype(str).str.replace(',', '.').astype(float)

# 3. Tri des données
# Il est crucial que les données soient triées par identifiant puis par date
df = df.sort_values(by=['identifiant', 'horodate'])

# 4. Détection des "trous"
# On calcule le temps écoulé depuis la ligne précédente pour chaque identifiant
df['prev_horodate'] = df.groupby('identifiant')['horodate'].shift(1)
df['diff'] = df['horodate'] - df['prev_horodate']

# On définit le seuil d'une heure
seuil = pd.Timedelta(hours=1)

# On filtre les lignes où l'écart est supérieur à 1 heure
mask_gaps = df['diff'] > seuil

# 5. Création des nouvelles lignes à insérer
# Pour chaque trou détecté, on crée une ligne 1h après la mesure précédente
lignes_ajout = df[mask_gaps].copy()
lignes_ajout['horodate'] = lignes_ajout['prev_horodate'] + seuil
lignes_ajout['pluie_mm'] = 0.0

# On ne garde que les colonnes utiles
cols = ['identifiant', 'horodate', 'pluie_mm']
df_base = df[cols]
df_ajout_clean = lignes_ajout[cols]

# 6. Fusion et sauvegarde
# On ajoute les nouvelles lignes au dataframe original
df_final = pd.concat([df_base, df_ajout_clean])

# On retrie le tout pour insérer les nouvelles lignes au bon endroit chronologique
df_final = df_final.sort_values(by=['identifiant', 'horodate'])

# Export du résultat en CSV (avec séparateur point-virgule et virgule pour les décimales)
df_final.to_csv(fichier_sortie, sep=';', decimal=',', index=False)

print(f"Traitement terminé. {len(df_ajout_clean)} lignes ont été ajoutées.")
print(f"Fichier sauvegardé sous : {fichier_sortie}")