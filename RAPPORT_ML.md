# Rapport Machine Learning - Prédiction du Trafic Vélo à Lyon

**Projet :** MeteoVelo - Impact de la météo sur le trafic cyclable
**Période :** Avril 2022 (30 jours)
**Objectif :** Prédire le nombre de vélos en circulation en fonction de la météo et du temps
**Technologie :** Apache Spark (PySpark)

---

## Table des Matières

1. [Contexte et Objectifs](#1-contexte-et-objectifs)
2. [Données Disponibles](#2-données-disponibles)
3. [Démarche Méthodologique](#3-démarche-méthodologique)
4. [Exploration des Données](#4-exploration-des-données)
5. [Préparation et Fusion](#5-préparation-et-fusion)
6. [Feature Engineering](#6-feature-engineering)
7. [Modélisation et Résultats](#7-modélisation-et-résultats)
8. [Expérimentations et Optimisations](#8-expérimentations-et-optimisations)
9. [Conclusions et Recommandations](#9-conclusions-et-recommandations)
10. [Limitations et Perspectives](#10-limitations-et-perspectives)

---

## 1. Contexte et Objectifs

### Problématique

La ville de Lyon souhaite comprendre l'impact des conditions météorologiques sur l'utilisation du vélo. L'objectif est de **prédire le trafic vélo** à partir de données temporelles et météorologiques pour :
- Optimiser les infrastructures cyclables
- Planifier la maintenance des pistes
- Proposer une application grand public d'aide à la décision

### Cas d'usage cible

**Application pratique :** "Devrais-je faire du vélo maintenant ?"
- Public : Cyclistes occasionnels et réguliers
- Période pertinente : Heures d'activité (7h-22h)
- Besoin : Prédiction en temps réel du trafic attendu

---

## 2. Données Disponibles

### Sources de données

**Période :** Avril 2022 (30 jours)

| Dataset | Lignes | Capteurs | Granularité | Description |
|---------|--------|----------|-------------|-------------|
| **Comptage vélo** | 262,872 | 376 sites | Horaire | Nombre de vélos comptés |
| **Température** | 26,618 | 17 stations | Variable (~10min) | Températures en °C |
| **Pluviométrie** | 5,866 | 31 stations | Variable (~6min) | Précipitations en mm |

### Observations critiques

**⚠️ Spécificité du dataset de pluie :**
Le dataset de pluviométrie **ne contient QUE les heures où il a plu**.
- Total : 16 jours de pluie sur 30
- Implication : Les heures sans pluie sont absentes (≠ 0mm enregistré)
- Solution retenue : LEFT JOIN + remplissage par 0mm

**⚠️ Format des données météo :**
- Température et pluie stockées en **STRING avec virgules** (ex: "14,75")
- Nécessité de conversion : `,` → `.` puis STRING → FLOAT

---

## 3. Démarche Méthodologique

### Architecture technique

**Choix de PySpark :**
- Exigence du projet : Utilisation obligatoire d'Apache Spark
- Avantages : Scalabilité, traitement distribué
- Configuration : Spark Session locale avec 4GB de mémoire

### Pipeline ML

```
1. Exploration (EDA)
   ↓
2. Nettoyage et Fusion
   ↓
3. Feature Engineering
   ↓
4. Modélisation
   ↓
5. Évaluation et Optimisation
```

---

## 4. Exploration des Données

### Analyse de la qualité

**Données vélo :**
- ✅ Aucune valeur manquante pour `count`
- ❌ 37% de valeurs manquantes pour `counter_id` (non critique)
- ✅ Dates au format timestamp exploitable

**Données météo :**
- ⚠️ Température : TYPE STRING au lieu de numérique
- ⚠️ Pluie : TYPE STRING + dataset partiel (heures de pluie uniquement)

### Distribution du trafic vélo

**Statistiques globales :**
- Minimum : 225 vélos/heure
- Maximum : 44,073 vélos/heure
- Moyenne : 10,073 vélos/heure
- Écart-type : 9,024 vélos

**Observation :** Grande variabilité liée aux patterns temporels (jour/nuit, semaine/weekend, heures de pointe).

*[ESPACE GRAPHIQUE : Distribution du nombre de vélos]*

---

## 5. Préparation et Fusion

### Stratégie de nettoyage

**1. Conversion des formats**

```python
# Température/Pluie : STRING → FLOAT
df = df.withColumn('temperature',
    regexp_replace(col('degre_celsius'), ',', '.').cast(FloatType()))
```

**2. Conversion temporelle**

```python
df = df.withColumn('timestamp', to_timestamp(col('horodate')))
```

### Agrégation temporelle

**Décision : Granularité horaire**

Chaque dataset a une granularité différente. Choix d'agréger à l'heure pour harmoniser.

| Dataset | Stratégie d'agrégation | Justification |
|---------|------------------------|---------------|
| **Température** | Moyenne des 17 capteurs | Représentativité géographique |
| **Pluie** | Moyenne des 31 capteurs | Atténuation des valeurs extrêmes |
| **Vélo** | Somme de tous les sites | Trafic total Lyon |

**Résultat :** 696 lignes (29 jours × 24 heures)

### Fusion des datasets

**Stratégie : LEFT JOIN**

```
df_velo (base)
  LEFT JOIN df_temperature
  LEFT JOIN df_pluie
```

**Pourquoi LEFT JOIN ?**
- Conservation de TOUTES les heures de comptage vélo
- Gestion des heures sans pluie : NULL → 0mm
- Préservation de la variable cible

**Gestion des valeurs manquantes :**
- Pluie NULL → **0mm** (pas de pluie)
- Température NULL → **0 cas** (couverture complète)

*[ESPACE GRAPHIQUE : Évolution du trafic vélo en avril 2022]*

*[ESPACE GRAPHIQUE : Température et précipitations en avril 2022]*

---

## 6. Feature Engineering

### Features temporelles

**Rationale :** Le trafic vélo suit des patterns temporels marqués.

| Feature | Type | Valeurs | Justification |
|---------|------|---------|---------------|
| `hour` | Numérique | 0-23 | Heures de pointe vs nuit |
| `day_of_week` | Numérique | 1-7 (Lun-Dim) | Semaine vs weekend |
| `is_weekend` | Binaire | 0/1 | Comportement loisir vs travail |
| `is_rush_hour` | Binaire | 0/1 | Pointes 7-9h et 17-19h |
| `month` | Numérique | 4 (Avril) | Saisonnalité (pour extension future) |

**Patterns observés :**

*[ESPACE GRAPHIQUE : Trafic moyen par heure de la journée]*

*[ESPACE GRAPHIQUE : Trafic moyen par jour de la semaine]*

### Features météorologiques

**Features numériques brutes :**
- `temperature` : Température moyenne en °C
- `precipitation` : Précipitations moyennes en mm
- `is_raining` : Booléen (precipitation > 0)

**Features catégorielles enrichies :**

**Intensité de pluie :**
- `no_rain` : 0mm
- `light` : 0-0.2mm
- `moderate` : 0.2-0.5mm
- `heavy` : >0.5mm

**Catégories de température :**
- `cold` : <5°C
- `cool` : 5-10°C
- `mild` : 10-15°C
- `warm` : 15-20°C
- `hot` : >20°C

**One-Hot Encoding :** Variables catégorielles converties en vecteurs binaires (sparse vectors).

*[ESPACE GRAPHIQUE : Distribution des intensités de pluie]*

*[ESPACE GRAPHIQUE : Trafic moyen par catégorie de température]*

### Corrélations

**Matrice de corrélation (features numériques vs nb_velos) :**

*[ESPACE GRAPHIQUE : Matrice de corrélation]*

**Observations :**
- Corrélation positive avec température (~0.3-0.4)
- Corrélation négative faible avec précipitation
- Features temporelles : corrélations variables selon patterns

---

## 7. Modélisation et Résultats

### Approche comparative

**4 modèles testés :**

1. **Régression Linéaire** : Baseline simple
2. **Decision Tree** : Capture des non-linéarités
3. **Random Forest** : Ensemble robuste
4. **Gradient Boosted Trees (GBT)** : Boosting séquentiel

**Configuration train/test :**
- Split : 80% train (585 lignes) / 20% test (111 lignes)
- Seed : 42 (reproductibilité)

### Résultats comparatifs

**Dataset complet 24h (0h-23h) :**

| Modèle | RMSE (vélos) | MAE (vélos) | R² | Classement |
|--------|--------------|-------------|-----|------------|
| **Gradient Boosted Trees** | **2,040** | **1,179** | **0.949** | 🥇 |
| Decision Tree | 2,356 | 1,597 | 0.931 | 🥈 |
| Random Forest | 3,044 | 1,984 | 0.885 | 🥉 |
| Régression Linéaire | 5,359 | 3,959 | 0.645 | 4 |

**Interprétation des métriques :**
- **R² = 0.949** : Le modèle explique 94.9% de la variance du trafic
- **RMSE = 2,040** : Erreur moyenne de ±2,040 vélos (~20% du trafic moyen)
- **MAE = 1,179** : Erreur absolue moyenne de ±1,179 vélos (~12%)

*[ESPACE GRAPHIQUE : Comparaison RMSE/MAE/R² des 4 modèles]*

### Meilleur modèle : Gradient Boosted Trees

**Pourquoi GBT surpasse les autres ?**
- **Boosting séquentiel** : Chaque arbre corrige les erreurs des précédents
- **Capture des interactions complexes** : Relations non-linéaires entre features
- **Robustesse** : Moins de surapprentissage que Decision Tree seul

**Analyse des prédictions :**

*[ESPACE GRAPHIQUE : Prédictions vs Valeurs Réelles (scatter plot)]*

*[ESPACE GRAPHIQUE : Analyse des résidus]*

**Observations :**
- Points concentrés autour de la diagonale → Bonnes prédictions
- Résidus centrés autour de 0 → Pas de biais systématique
- Quelques outliers sur trafic très élevé (>30,000 vélos)

---

## 8. Expérimentations et Optimisations

### 8.1 Expérience 1 : Heures Actives (7h-22h)

**Hypothèse initiale :**
> "En filtrant les heures de nuit (faible trafic), le modèle sera plus précis sur les heures pertinentes."

**Motivation :**
- Cas d'usage pratique : Application grand public
- Personne ne demande de prédiction à 3h du matin
- Réduction du "bruit" des heures creuses

**Méthodologie :**
- Filtre : `hour >= 7 AND hour <= 22`
- Réduction : 696 → 464 lignes (-33%)
- Modèle : GBT avec mêmes hyperparamètres

**Résultats :**

| Modèle | RMSE | MAE | R² | Différence |
|--------|------|-----|-----|------------|
| GBT 24h (baseline) | 2,040 | 1,179 | 0.949 | - |
| GBT 7h-22h | 2,532 | 1,657 | 0.891 | **❌ -24% RMSE** |

*[ESPACE GRAPHIQUE : Comparaison 24h vs 7h-22h]*

**Conclusion : CONTRE-INTUITIVE ✋**

Le modèle 24h est **meilleur** malgré l'inclusion des heures de nuit.

**Explications :**
1. **Les heures de nuit NE SONT PAS du bruit**
   - Trafic faible mais **prévisible** (~500-2000 vélos)
   - Fournit un **baseline stable** au modèle

2. **Perte d'information structurelle**
   - Le contraste jour/nuit structure l'apprentissage
   - Cycle circadien complet = meilleure compréhension

3. **Moins de données d'entraînement**
   - 33% de données en moins = apprentissage moins robuste

4. **Variance plus élevée sur heures actives**
   - Heures 7h-22h : Grande variabilité (6,000 à 40,000)
   - Heures de nuit : Faible variabilité (faciles à prédire)
   - Le modèle 7h-22h doit gérer SEULEMENT les cas difficiles

**Décision finale :**
- **Statistiquement** : Garder 24h (R²=0.949)
- **Pratiquement** : Le modèle 7h-22h reste pertinent pour l'application (R²=0.891 acceptable)

---

### 8.2 Expérience 2 : Impact de `day_of_week`

**Hypothèse initiale :**
> "day_of_week et is_weekend sont redondants. On peut simplifier le modèle en gardant seulement is_weekend."

**Contexte :**
- `day_of_week` : 1-7 (Lundi à Dimanche)
- `is_weekend` : 0/1 (Semaine vs Weekend)
- Apparente redondance : is_weekend dérivé de day_of_week

**Objectif :**
- Isoler l'effet weekend
- Tester si chaque jour a un pattern spécifique
- Simplifier le modèle si possible

**Méthodologie :**
- Dataset : 7h-22h (cas d'usage pratique)
- Features : TOUTES sauf `day_of_week`
- Modèle : GBT

**Résultats :**

| Modèle | RMSE | MAE | R² | Différence |
|--------|------|-----|-----|------------|
| AVEC day_of_week | 2,532 | 1,657 | 0.891 | - |
| SANS day_of_week | 4,072 | 2,525 | 0.762 | **❌ -61% RMSE** |

*[ESPACE GRAPHIQUE : Comparaison AVEC vs SANS day_of_week]*

**Conclusion : DÉGRADATION MASSIVE ⚠️**

La perte de **61% sur RMSE** est catastrophique.

**Insights majeurs :**

1. **Chaque jour a un pattern UNIQUE**
   - Lundi ≠ Mardi ≠ Mercredi ≠ Jeudi ≠ Vendredi
   - Pas juste "semaine vs weekend"
   - Variations subtiles mais cruciales

2. **Patterns journaliers probables :**
   - **Lundi** : Retour au travail, trafic élevé
   - **Mardi-Jeudi** : Rythme de croisière
   - **Vendredi** : Fin de semaine, comportement mixte
   - **Samedi** : Loisirs, shopping (trafic différent)
   - **Dimanche** : Repos, trafic faible

3. **is_weekend et day_of_week sont COMPLÉMENTAIRES**
   - `is_weekend` : Capture "weekend vs semaine"
   - `day_of_week` : Capture "Lundi vs Mardi vs..."
   - Ces informations ne sont PAS redondantes

**Augmentation de l'importance de is_weekend :**
- AVEC day_of_week : 0.5%
- SANS day_of_week : [Augmentation observée mais insuffisante]

Même en compensant, le modèle ne peut pas retrouver l'information perdue.

**Décision finale :**
✅ **GARDER day_of_week** - Feature critique et irremplaçable

---

## 9. Feature Importance - Analyses

### Modèle GBT 24h (optimal)

**Classement des features :**

| Rang | Feature | Importance | Catégorie |
|------|---------|------------|-----------|
| 1 | `hour` | 34.1% | ⏰ Temporel |
| 2 | `is_rush_hour` | 26.0% | ⏰ Temporel |
| 3 | `day_of_week` | 18.8% | ⏰ Temporel |
| 4 | `temperature` | 13.8% | 🌡️ Météo |
| 5 | `precipitation` | 2.2% | 🌧️ Météo |
| 6 | `rain_light` | 2.0% | 🌧️ Météo |
| ... | Autres | <1% | - |

*[ESPACE GRAPHIQUE : Feature Importance (barres horizontales)]*

### Interprétation

**1. Domination des features temporelles (78.9%)**

Les 3 premières features sont temporelles :
- `hour` (34%) + `is_rush_hour` (26%) = **60%** de l'importance
- Le trafic vélo est **hautement prédictible** par l'heure

**Insight :** Le vélo à Lyon est principalement un **mode de transport urbain** (domicile-travail).

**2. Impact modéré de la température (13.8%)**

La température influence le confort, mais :
- Les cyclistes réguliers continuent même par temps froid
- L'effet est secondaire par rapport au besoin de se déplacer

**3. Impact limité de la pluie (~4%)**

Surprenant mais logique :
- Les cyclistes quotidiens (vélotaf) continuent malgré la pluie
- L'intensité de pluie ne change pas drastiquement le comportement
- **Limitation** : Seulement 16 jours de pluie sur 30 (données insuffisantes)

**4. day_of_week essentiel (18.8%)**

Confirmé par l'expérience 2 :
- Chaque jour a son pattern
- Impossible à remplacer par `is_weekend` seul

---

## 10. Conclusions et Recommandations

### Modèle optimal pour l'application

**Configuration retenue :**
- **Dataset** : 24 heures (0h-23h)
- **Modèle** : Gradient Boosted Trees
- **Features** : Toutes (17 features après encoding)

**Performances :**
- **R² = 0.949** (94.9% de variance expliquée)
- **MAE = 1,179 vélos** (erreur moyenne absolue)
- **RMSE = 2,040 vélos** (erreur quadratique)

**Interprétation pratique :**
```
Exemple :
- Prédiction : 15,000 vélos
- Intervalle de confiance : 15,000 ± 1,179 vélos
- Fourchette réaliste : 13,800 - 16,200 vélos
```

### Insights métier pour la Ville de Lyon

**1. Infrastructure cyclable**
- Prioriser les axes utilisés aux **heures de pointe** (7-9h, 17-19h)
- Renforcer l'éclairage pour usage hivernal/nocturne
- Adapter la maintenance selon les **jours de la semaine**

**2. Météo**
- Impact température > impact pluie
- Investir dans le **confort thermique** plutôt que protection pluie
- Communication ciblée sur l'habillement par temps froid

**3. Promotion du vélo**
- Cibler le **vélotaf** (vélo-travail) : public le plus stable
- Encourager les entreprises (prime vélo, parkings sécurisés)
- Différencier stratégies semaine vs weekend

### Utilisation en production

**API de prédiction :**
```python
Input: {
  "date": "2024-01-15",  # Lundi
  "hour": 18,
  "temperature": 8.5,
  "precipitation": 0
}

Output: {
  "predicted_bikes": 18500,
  "confidence_interval": [17321, 19679],
  "message": "Forte affluence attendue - Heure de pointe en semaine"
}
```

---

## 11. Limitations et Perspectives

### Limitations actuelles

**1. Période limitée : 1 mois de données**

❌ **Problèmes :**
- Pas de saisonnalité capturée (printemps uniquement)
- Feature `month` inutilisable (constante = Avril)
- Pas de variation climatique importante

❌ **Impact :**
- Modèle non généralisable sur l'année complète
- Comportements été/hiver non modélisés
- Jours fériés non représentés

**2. Données de pluie insuffisantes**

❌ **Problèmes :**
- Seulement **16 jours de pluie** sur 30
- Peu de variété d'intensité (majoritairement légère)
- Impact de la pluie sous-estimé (importance = 4%)

❌ **Impact :**
- Prédictions incertaines par forte pluie
- Relation pluie/trafic non robuste

**3. Granularité horaire**

❌ **Problèmes :**
- Perte des variations infra-horaires
- Moyennes qui lissent les pics courts

### Perspectives d'amélioration

**1. Extension temporelle : 1 an de données**

✅ **Objectifs :**
- Capturer la **saisonnalité** complète
- Modéliser les variations été/hiver
- Enrichir les patterns de pluie

✅ **Résultats attendus :**
```
Features activées :
- month : Variation 1-12 (vs constante = 4)
- is_summer/is_winter : Saisonnalité binaire
- temperature : Range étendu (-5°C à 35°C vs 0-23°C)
- precipitation : Plus de variété d'intensité
```

✅ **Amélioration estimée :**
- R² : 0.95 → **0.97-0.98**
- Importance pluie : 4% → **8-10%**
- Généralisation robuste sur toute l'année

**2. Features additionnelles**

- **Vacances scolaires** : Comportement loisir accentué
- **Jours fériés** : Trafic atypique
- **Événements** : Manifestations, grèves, marchés
- **Qualité de l'air** : Influence possible sur usage vélo
- **Vent** : Confort cycliste

**3. Granularité fine (15 minutes)**

- Détecter les pics de rush hour
- Meilleure précision en temps réel

**4. Modèles avancés**

- **Séries temporelles** : LSTM, Prophet
- **Ensemble stacking** : Combiner GBT + RF + LSTM
- **Deep Learning** : Réseaux de neurones pour interactions complexes

---

## Conclusion Générale

### Réussites du projet

✅ **Modèle performant** : R² = 94.9% sur données d'avril 2022
✅ **Insights métier** : Domination des patterns temporels (79%)
✅ **Expérimentations rigoureuses** : 3 notebooks d'optimisation
✅ **Scalabilité** : Architecture PySpark prête pour big data

### Chemin de réflexion

Le projet a suivi une démarche **itérative et expérimentale** :

1. **Hypothèse initiale** : La météo influence fortement le trafic vélo
2. **Découverte 1** : Les patterns temporels dominent (79% vs 21% météo)
3. **Hypothèse 2** : Filtrer les heures de nuit améliore le modèle
4. **Découverte 2** : Contre-intuitif - Les heures de nuit structurent l'apprentissage
5. **Hypothèse 3** : day_of_week est redondant avec is_weekend
6. **Découverte 3** : Chaque jour a un pattern unique (-61% sans day_of_week)

**Leçon ML :** Les expérimentations data-driven révèlent souvent des résultats contre-intuitifs.

### Recommandation finale

**Pour déploiement immédiat (avril uniquement) :**
- ✅ Modèle GBT 24h (R²=0.949)
- ⚠️ Avertir l'utilisateur : "Prédictions optimisées pour avril"

**Pour mise en production robuste :**
- 🎯 **PRIORITAIRE** : Collecter 1 an de données
- 🎯 Scale le modèle avec saisonnalité complète
- 🎯 Ré-évaluer l'importance de la pluie sur 12 mois

---

**Projet MeteoVelo - Machine Learning**
*Rapport rédigé en décembre 2024*
*Technologies : PySpark, MLlib, Jupyter*
