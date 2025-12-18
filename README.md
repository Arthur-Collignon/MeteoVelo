# Analyse et Prédiction de l'Impact Météorologique sur la Mobilité Cycliste à Lyon

## 1. Présentation Générale et Objectifs

L'objectif principal est de comprendre comment les conditions météorologiques influencent les habitudes de déplacement à vélo dans la métropole de Lyon et de construire un modèle prédictif pour anticiper la demande future.

Le projet s'articule autour de deux axes majeurs :

* **L'Analyse Descriptive (Business Intelligence) :** Quantifier l'impact réel de la pluie, de la température et des saisons sur les cyclistes (vérification d'hypothèses).
* **L'Analyse Prédictive (Machine Learning) :** Créer un modèle capable d'estimer le volume de cyclistes attendu en fonction des prévisions météo.

> **Période de test et développement :** Les données utilisées couvrent la période du **2023-04-01 au 2023-04-30** (Note : ajusté à 30 jours car avril n'en compte pas 31).

---

## 2. Préparation et Nettoyage des Données (Data Engineering)

Nous disposons de deux sources qu'il faudra fusionner.

### Nettoyage des données Vélo

* **Gestion des valeurs manquantes :** Traitement des pannes de compteurs.
* **Traitement des valeurs aberrantes :** Identification des compteurs bloqués ou événements exceptionnels (ex: baisse drastique due au confinement COVID).
* **Harmonisation temporelle :** Assurance que les données sont au même pas de temps (ex: agrégation par heure ou par jour).

### Nettoyage des données Météo

* **Sélection des features pertinentes :** Précipitations (mm), Température (°C).

### Nettoyage des données des sites de comptages

* Filtrage pour ne conserver que les sites de comptages de vélos et la data correspondante.

### Fusion

Création d'un dataset unique où chaque ligne correspond à un moment précis contenant le nombre de vélos **ET** la météo.

* *Exemple :* `2023-05-12 08:00:00` | `Nb_Vélos` | `Météo`

---

## 3. Analyse Exploratoire (EDA) & Vérification d'Hypothèses

Visualisation des données pour comprendre les tendances passées.

### A. Tendance Globale

* **Évolution :** Visualiser le trafic vélo sur plusieurs années.
* **Saisonnalité :** Identifier les pics en été vs les creux en hiver.
* **Tendance de fond :** Analyser si l'usage du vélo augmente globalement à Lyon d'une année sur l'autre (indépendamment de la météo).

### B. Impact de la Météo

* **Corrélation Pluie/Trafic :** Graphiques montrant le volume de vélos selon la quantité de pluie.
* *Objectif :* Calculer le % de baisse moyen (ex: "Une pluie faible entraîne **-20%** de trafic, une forte pluie **-60%**").


* **Corrélation Température/Trafic :** Recherche d'un seuil critique (ex: chute brutale en dessous de 5°C).
* **Matrice de Corrélation :** Utilisation d'une *heatmap* pour identifier la variable météo la plus impactante (Pluie vs Froid).

---

## 4. Modélisation Prédictive (Machine Learning)

Entraînement d'un algorithme pour apprendre les relations mathématiques entre la météo et le nombre de vélos.

### Choix des variables (Features)

* **Météo :** Pluie, Température, Vent.
* **Temporelles :** Heure de la journée, Jour de la semaine (lundi vs dimanche), Mois, Vacances scolaires, Jours fériés.

### Choix du Modèle

* **Régression Linéaire :** Pour une approche simple et explicable.


* **Random Forest :** Pour capturer des relations non-linéaires complexes (ex: la pluie dérange moins s'il fait très chaud en été que s'il fait 2°C en hiver).

### Entraînement et Test

Utilisation de la méthode **Train/Test Split** : les premières années pour entraîner le modèle et la dernière année pour valider les prédictions.

---

## Datasets et Ressources

### Température

* [Températures en temps réel (Data Gouv)](https://www.data.gouv.fr/datasets/temperatures-en-temps-reel-sur-la-metropole-de-lyon/reuses_and_dataservices)
* [Emplacement et état des capteurs (Grand Lyon)](https://data.grandlyon.com/portail/fr/jeux-de-donnees/emplacement-et-etat-des-capteurs-de-temperature-en-temps-reel-dans-la-metropole-de-lyon/api)

### Pluie

* [Mesures de pluviométrie (Grand Lyon)](https://data.grandlyon.com/portail/fr/jeux-de-donnees/mesures-de-pluviometrie-de-la-metropole-de-lyon/api)

### Vélo

* [Mesures de comptage (Grand Lyon)](https://data.grandlyon.com/portail/fr/jeux-de-donnees/mesures-comptage-metropole-lyon/api)

