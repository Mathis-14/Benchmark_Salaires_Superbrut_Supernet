# Benchmark Salaires : Brut vs Net, Superbrut vs Supernet
# BENCHMARK 1

## 📋 Objectif

Ce projet vise à analyser et comparer les différents niveaux de salaires en France :
- **Brut** : Salaire brut annoncé
- **Net** : Salaire net avant impôt sur le revenu
- **Superbrut** : Coût total employeur (brut + cotisations patronales)
- **Supernet** : Salaire net après impôt sur le revenu (ce que le salarié reçoit réellement)

L'objectif est de comprendre l'écart réel entre ce que l'employeur paie et ce que le salarié perçoit, en tenant compte de toutes les cotisations sociales et de l'impôt sur le revenu.

## 🔧 Méthodologie

### 1. Collecte des données

Le script `script.py` utilise l'API publique de [mon-entreprise.urssaf.fr](https://mon-entreprise.urssaf.fr) pour calculer les différents montants de salaires selon la législation française en vigueur.

**Paramètres utilisés :**
- Calcul automatique de l'impôt sur le revenu via l'API (barème progressif 2024)
- 1 part fiscale (célibataire)
- Statut : non-cadre
- Gestion du temps partiel pour les bas salaires (< SMIC)

**Plage analysée :** De 1 000€ à 500 000€ de salaire brut annuel, par paliers de 1 000€ (500 points de données).

### 2. Calculs effectués

Pour chaque salaire brut, l'API calcule :
1. **Coût total employeur (Superbrut)** : Brut + cotisations patronales
2. **Salaire brut** : Montant de base
3. **Salaire net avant impôt** : Brut - cotisations salariales
4. **Salaire net après impôt (Supernet)** : Net avant impôt - impôt sur le revenu
5. **Montant de l'impôt** : Calculé selon le barème progressif français

### 3. Visualisations

Le script `plot.py` génère 8 graphiques dans le dossier `graphs/` :
- Taux net effectif (net / brut)
- Taux supernet effectif (supernet / superbrut)
- Superbrut → Supernet reconstruit
- Superbrut → Net (avant impôt)
- Comparaison Brut vs Superbrut
- Impact de l'impôt (Net avant vs après impôt)
- Taux d'imposition effectif
- Comparaison Brut vs Supernet

## 📊 Résultats et Statistiques

### Statistiques globales

- **Plage analysée** : 1 000€ à 500 000€ de salaire brut annuel
- **Nombre de points de données** : 500

### Taux moyens observés

- **Taux net/brut moyen** : **79,78%**
  - Le salarié perçoit en moyenne ~80% de son salaire brut (avant impôt)
  REMARQUE : Ce taux n'est pas pertinent car il ne reflète pas la richesse réelle dépensée ou perçue par respectivement l'employeur/l'employé => d'où nécessité d'intégrer le superbrut et le supernet.
  
- **Taux supernet/superbrut moyen** : **40,65%**
  - Le salarié perçoit en moyenne seulement **40,65%** de ce que l'employeur paie réellement
    Voir graphe taux taux_supernet_effectif_supernet_sur_superbrut
    Pour 15 000 € de coût réel employeur (superbrut) → ~74% revient à l'employé
    Pour 50 000€ de coût réel emplpoyeur (superbrut) → ~54% revient à l'employé
    Pour 500 000€ de coût employeur → ~36% revient à l'employé

  
- **Taux d'imposition moyen** (sur salaires imposables) : **30,42%**
  - Sur le salaire net avant impôt, l'impôt représente en moyenne 30,42%

### Écarts moyens

- **Écart brut/superbrut** : +39,2% en moyenne
  - L'employeur paie en moyenne 39,2% de plus que le salaire brut annoncé
  
- **Écart brut/supernet** : -43,9% en moyenne
  - Le salarié perçoit en moyenne 43,9% de moins que son salaire brut annoncé

### Exemples par paliers de salaire

| Salaire Brut | Superbrut | Net (avant impôt) | Supernet (après impôt) | Impôt | Taux Supernet/Superbrut |
|--------------|-----------|-------------------|------------------------|-------|-------------------------|
| **30 000€** | 38 309€ | 23 485€ | 22 144€ | 1 341€ | **57,8%** |
| **50 000€** | 72 277€ | 40 083€ | 34 772€ | 5 311€ | **48,1%** |
| **80 000€** | 114 655€ | 63 344€ | 51 055€ | 12 289€ | **44,5%** |
| **100 000€** | 143 248€ | 79 386€ | 62 284€ | 17 102€ | **43,5%** |
| **150 000€** | 214 731€ | 119 491€ | 86 271€ | 33 220€ | **40,2%** |
| **200 000€** | 285 721€ | 159 576€ | 109 921€ | 49 655€ | **38,5%** |
| **300 000€** | 424 437€ | 239 616€ | 154 644€ | 84 972€ | **36,4%** |
| **500 000€** | 683 660€ | 411 844€ | 249 369€ | 162 474€ | **36,5%** |

### Taux supernet/superbrut par tranche de salaire

Le taux de conversion entre superbrut et supernet **diminue** avec l'augmentation du salaire :

| Tranche de salaire brut | Taux Supernet/Superbrut moyen |
|-------------------------|-------------------------------|
| 0€ - 30 000€ | **67,8%** |
| 30 000€ - 50 000€ | **53,0%** |
| 50 000€ - 80 000€ | **46,3%** |
| 80 000€ - 150 000€ | **42,4%** |
| 150 000€ - 300 000€ | **38,0%** |
| 300 000€ - 500 000€ | **36,0%** |

## 💡 Conclusions et Insights

### 1. L'écart réel est considérable

Pour un salaire brut de **100 000€** :
- L'employeur paie réellement **143 248€** (superbrut)
- Le salarié perçoit **62 284€** (supernet)
- **L'écart total est de 80 964€** (56,5% du superbrut)

### 2. Le taux supernet/superbrut diminue avec le salaire

Plus le salaire est élevé, plus la part perçue par le salarié diminue :
- **Bas salaires** (< 30k€) : ~68% du superbrut est perçu
- **Hauts salaires** (> 300k€) : seulement ~36% du superbrut est perçu

Cette diminution s'explique par :
- La progressivité de l'impôt sur le revenu
- Les cotisations sociales qui restent proportionnelles

### 3. L'impact de l'impôt devient significatif à partir de 30k€

- En dessous de 15 000€ brut/an : pas d'impôt sur le revenu
- À partir de 30 000€ : l'impôt représente déjà 5,7% du net avant impôt
- À 100 000€ : l'impôt représente 21,5% du net avant impôt
- À 500 000€ : l'impôt représente 39,4% du net avant impôt

### 4. Le "coût employeur" est systématiquement sous-estimé

L'écart entre brut et superbrut est constant (~39%) et représente un coût réel important pour l'employeur qui n'est pas toujours bien compris par les salariés.

### 5. Le "salaire net" annoncé est trompeur

Le salaire net avant impôt ne reflète pas ce que le salarié perçoit réellement. Pour un salaire de 100k€ brut :
- Net avant impôt : 79 386€
- Supernet réel : 62 284€
- **Écart de 17 102€** (21,5% du net avant impôt)

## 🚀 Utilisation

### Prérequis

```bash
pip install pandas matplotlib requests
```

### Génération des données

```bash
python script.py
```

Génère le fichier `mon_entreprise_grille_salaires.csv` avec tous les calculs.

### Génération des graphiques

```bash
python plot.py
```

Génère les 7 graphiques dans le dossier `graphs/`.

## 📁 Structure des fichiers

```
benchmark1/
├── script.py                          # Script de calcul des salaires
├── plot.py                            # Script de génération des graphiques
├── mon_entreprise_grille_salaires.csv # Données calculées
├── graphs/                            # Graphiques générés
│   ├── brut_vs_superbrut.png
│   ├── brut_vs_supernet.png
│   ├── impact_impot.png
│   ├── superbrut_vers_net.png
│   ├── superbrut_vers_supernet_reconstruit.png
│   ├── taux_imposition.png
│   ├── taux_net_effectif_net_sur_brut.png
│   └── taux_supernet_effectif_supernet_sur_superbrut.png
└── README.md                          # Ce fichier
```

## 📝 Notes techniques

- Les calculs utilisent l'API publique de mon-entreprise.urssaf.fr
- Barème d'impôt sur le revenu 2024 (revenus 2023)
- Configuration : 1 part fiscale (célibataire), statut non-cadre
- Les calculs incluent toutes les cotisations sociales obligatoires
- Gestion automatique du temps partiel pour les salaires < SMIC

## 🔄 Mise à jour

Pour mettre à jour les données avec les nouveaux barèmes :
1. Vérifier que l'API mon-entreprise.urssaf.fr est à jour
2. Relancer `script.py` pour régénérer le CSV
3. Relancer `plot.py` pour régénérer les graphiques

---

**Dernière mise à jour** : Analyse basée sur la législation française 2024

