# Plan Machine Learning - MeteoVelo

## Objectif
Créer un modèle prédictif pour estimer le volume de cyclistes en fonction des conditions météorologiques et temporelles.

---

## Étape 1: Exploration des Données (EDA)

### 1.1 Chargement et Inspection
- [ ] Charger les 3 datasets:
  - `counting_data_april_2022.csv` (données vélo)
  - `temperature_converted.csv` (températures)
  - `eau_converted.csv` (pluviométrie)
- [ ] Vérifier la structure de chaque dataset
- [ ] Identifier les colonnes clés pour la fusion
- [ ] Analyser les types de données et formats de dates

### 1.2 Analyse Qualité des Données
- [ ] Détecter les valeurs manquantes (NaN)
- [ ] Identifier les valeurs aberrantes (outliers)
- [ ] Vérifier la cohérence temporelle
- [ ] Analyser la distribution des variables

### 1.3 Visualisations Exploratoires
- [ ] Distribution du nombre de vélos par heure/jour
- [ ] Distribution de la température
- [ ] Distribution des précipitations
- [ ] Patterns temporels (tendances jour/semaine)

---

## Étape 2: Préparation et Fusion des Données

### 2.1 Prétraitement des Données Vélo
- [ ] Convertir les dates au bon format (datetime)
- [ ] Agréger les comptages par période (heure/jour)
- [ ] Gérer les valeurs manquantes (interpolation ou suppression)
- [ ] Créer une variable cible: `nb_velos_total`

### 2.2 Prétraitement des Données Météo
- [ ] Harmoniser les timestamps (même format que les données vélo)
- [ ] Gérer les valeurs manquantes météo
- [ ] Vérifier la cohérence des mesures (pas de températures impossibles)

### 2.3 Fusion des Datasets
- [ ] Merger les données vélo + température (sur timestamp)
- [ ] Merger avec les données de pluviométrie
- [ ] Vérifier l'intégrité après fusion
- [ ] Créer le dataset final `data_merged.csv`

**Résultat attendu:** Un dataset unique avec colonnes:
- `timestamp` (datetime)
- `nb_velos` (target)
- `temperature` (°C)
- `precipitation` (mm)
- + autres features météo si disponibles

---

## Étape 3: Feature Engineering

### 3.1 Features Temporelles
- [ ] `hour` : Heure de la journée (0-23)
- [ ] `day_of_week` : Jour de la semaine (0=Lundi, 6=Dimanche)
- [ ] `is_weekend` : Booléen (Samedi/Dimanche)
- [ ] `month` : Mois (1-12)
- [ ] `is_rush_hour` : Booléen (7-9h et 17-19h)

### 3.2 Features Météo Enrichies
- [ ] `temp_category` : Catégories (froid < 5°C, doux 5-15°C, chaud > 15°C)
- [ ] `is_raining` : Booléen (précipitations > 0)
- [ ] `rain_intensity` : Catégories (faible/modérée/forte)

### 3.3 Features Calendaires (optionnel mais recommandé)
- [ ] `is_holiday` : Jours fériés français
- [ ] `is_school_vacation` : Vacances scolaires zone A (Lyon)

### 3.4 Encodage des Variables Catégorielles
- [ ] One-Hot Encoding pour `day_of_week`, `month`, etc.
- [ ] Label Encoding si nécessaire

---

## Étape 4: Modélisation

### 4.1 Préparation des Données
- [ ] Séparer Features (X) et Target (y)
- [ ] Train/Test Split (80/20 ou 70/30)
  - Option 1: Split aléatoire
  - Option 2: Split temporel (les 24 premiers jours pour train, les 6 derniers pour test)
- [ ] Normalisation/Standardisation des features numériques (si nécessaire)

### 4.2 Modèle Baseline: Régression Linéaire
- [ ] Entraîner une régression linéaire simple
- [ ] Prédire sur l'ensemble de test
- [ ] Calculer les métriques:
  - MAE (Mean Absolute Error)
  - RMSE (Root Mean Squared Error)
  - R² Score
- [ ] Analyser les coefficients (importance des features)

### 4.3 Modèle Avancé: Random Forest
- [ ] Entraîner un Random Forest Regressor
- [ ] Tester différents hyperparamètres:
  - `n_estimators` (nombre d'arbres: 50, 100, 200)
  - `max_depth` (profondeur max: None, 10, 20)
  - `min_samples_split` (2, 5, 10)
- [ ] Utiliser GridSearchCV ou RandomizedSearchCV pour l'optimisation
- [ ] Calculer les mêmes métriques que pour la baseline

### 4.4 Modèles Supplémentaires (optionnel)
- [ ] XGBoost (si temps disponible)
- [ ] Gradient Boosting (si temps disponible)

---

## Étape 5: Évaluation et Analyse

### 5.1 Comparaison des Modèles
- [ ] Tableau comparatif des métriques (MAE, RMSE, R²)
- [ ] Graphiques: Prédictions vs Valeurs Réelles
- [ ] Analyse des résidus (erreurs)

### 5.2 Importance des Features
- [ ] Feature Importance du Random Forest
- [ ] Identifier les variables les plus impactantes:
  - Météo (température, pluie) vs Temporelles (heure, jour)

### 5.3 Interprétation Métier
- [ ] Quantifier l'impact de la pluie (% de baisse)
- [ ] Quantifier l'impact de la température
- [ ] Identifier les heures de pointe
- [ ] Identifier les jours avec le plus de cyclistes

---

## Étape 6: Visualisations et Insights

### 6.1 Graphiques Clés
- [ ] Corrélation Heatmap (toutes les variables)
- [ ] Impact de la pluie sur le trafic (bar plot)
- [ ] Impact de la température (scatter plot)
- [ ] Prédictions vs Réalité (ligne temporelle)
- [ ] Feature Importance (bar plot)

### 6.2 Insights Business
- [ ] Rédiger 3-5 insights clés pour les décideurs
  - Ex: "La pluie réduit le trafic vélo de X%"
  - Ex: "Les heures de pointe sont 8h et 18h"
  - Ex: "La température optimale est entre X et Y°C"

---

## Étape 7: Sauvegarde et Documentation

### 7.1 Sauvegarder les Résultats
- [ ] Exporter le dataset final: `data_merged.csv`
- [ ] Sauvegarder le meilleur modèle: `model_final.pkl` (joblib)
- [ ] Créer un fichier de résultats: `results.json` avec les métriques

### 7.2 Notebook Final
- [ ] Organiser le notebook en sections claires
- [ ] Ajouter des commentaires et markdown explicatifs
- [ ] Nettoyer le code (supprimer les cellules inutiles)
- [ ] Vérifier que tout est reproductible

### 7.3 Documentation
- [ ] README.md ou rapport final avec:
  - Méthodologie
  - Résultats principaux
  - Graphiques clés
  - Conclusions

---

## Technologies et Bibliothèques

```python
# Data manipulation
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Machine Learning
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Sauvegarde
import joblib
import json
```

---

## Ordre de Priorité

1. **Phase 1 (Fondations):** Étapes 1 + 2 → Avoir un dataset propre et fusionné
2. **Phase 2 (Features):** Étape 3 → Créer les features temporelles et météo
3. **Phase 3 (Modèles):** Étape 4.1 + 4.2 → Baseline fonctionnelle
4. **Phase 4 (Amélioration):** Étape 4.3 → Random Forest optimisé
5. **Phase 5 (Finalisation):** Étapes 5 + 6 + 7 → Analyse et documentation

---

## Critères de Succès

- [ ] Dataset fusionné propre et exploitable
- [ ] Au moins 2 modèles fonctionnels (Linear + Random Forest)
- [ ] R² > 0.6 sur l'ensemble de test
- [ ] Insights métier clairs et visualisés
- [ ] Code propre et reproductible

---

## Questions à Résoudre en Cours de Route

1. Quel pas de temps utiliser? (heure vs jour)
2. Comment gérer les compteurs multiples? (agrégation spatiale)
3. Faut-il normaliser les features?
4. Train/Test split aléatoire ou temporel?
5. Quelles sont les features les plus importantes?

---

**Prêt à démarrer!** 🚴‍♂️
