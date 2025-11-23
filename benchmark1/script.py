import time, random, requests, pandas as pd, os
from pathlib import Path

# Définir le répertoire de base comme étant le répertoire du script (benchmark1)
BASE_DIR = Path(__file__).parent

API_URL = "https://mon-entreprise.urssaf.fr/api/v1/evaluate"

EXPRESSIONS = [
    "salarié . coût total employeur",
    "salarié . contrat . salaire brut",
    "salarié . rémunération . net . à payer avant impôt",
    "salarié . rémunération . net . payé après impôt",
    "impôt . montant",  # Pour vérifier que l'impôt est bien calculé
]

# ===== Hypothèses "cohérentes" / stables =====
# Option 1: Calcul automatique de l'impôt via l'API (si disponible)
USE_IMPOT_AUTO = True  # Si True, essaie d'utiliser le calcul de l'API, sinon calcule manuellement
# Option 2: Taux personnalisé (si vous voulez forcer un taux spécifique)
TAUX_IMPOT_PERSO = 8  # <-- mets ton taux ici (0 à 100) - utilisé seulement si USE_IMPOT_AUTO = False
# Paramètres fiscaux pour le calcul manuel de l'impôt
NOMBRE_PARTS_FISCALES = 1  # 1 = célibataire, 2 = couple, etc.
SMIC_BRUT_ANNUEL_2025 = 21621.60  # ordre de grandeur SMIC temps plein
# ===========================================

session = requests.Session()

def call_api(payload, max_retries=8):
    for attempt in range(max_retries):
        r = session.post(API_URL, json=payload, timeout=30)

        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            sleep_s = float(retry_after) if retry_after else (1.0 * (2 ** attempt) + random.random())
            time.sleep(sleep_s)
            continue

        r.raise_for_status()
        return r.json()

    raise RuntimeError("Trop de 429 d’affilée")

def to_annual(value, unit):
    if value is None or unit is None:
        return value
    if unit.get("numerators")==["€"] and unit.get("denominators")==["mois"]:
        return value * 12
    return value

def calculer_impot_revenu(revenu_imposable, nombre_parts=1):
    """
    Calcule l'impôt sur le revenu selon le barème progressif français 2024.
    
    Barème 2024 (revenus 2023):
    - Jusqu'à 11 294 € : 0%
    - De 11 294 € à 28 797 € : 11%
    - De 28 797 € à 82 341 € : 30%
    - De 82 341 € à 177 106 € : 41%
    - Au-delà de 177 106 € : 45%
    
    Args:
        revenu_imposable: Revenu imposable annuel (en €)
        nombre_parts: Nombre de parts fiscales (défaut: 1 pour célibataire)
    
    Returns:
        Montant de l'impôt annuel (en €)
    """
    # Quotient familial
    quotient_familial = revenu_imposable / nombre_parts
    
    # Barème 2024 (revenus 2023) - limites supérieures des tranches
    tranches = [11294, 28797, 82341, 177106, float('inf')]
    taux = [0.0, 0.11, 0.30, 0.41, 0.45]
    
    impot_quotient = 0.0
    reste = quotient_familial
    
    # Calcul progressif par tranche
    limite_precedente = 0
    for i in range(len(tranches)):
        if reste <= limite_precedente:
            break
        # Montant imposable dans cette tranche
        montant_tranche = min(reste - limite_precedente, tranches[i] - limite_precedente)
        if montant_tranche > 0:
            impot_quotient += montant_tranche * taux[i]
        limite_precedente = tranches[i]
    
    # Impôt total = impôt sur quotient × nombre de parts
    impot_total = impot_quotient * nombre_parts
    
    return max(0, impot_total)

def build_situation(brut_annuel):
    """
    Rend les bas salaires cohérents :
    - si brut < SMIC temps plein => on le modélise en temps partiel
      avec une quotité brut/SMIC (capée à 100%).
    """
    quotite = min(1.0, brut_annuel / SMIC_BRUT_ANNUEL_2025)
    temps_partiel = "oui" if quotite < 1.0 else "non"

    situation = {
        # entrée principale
        "salarié . contrat . salaire brut": f"{brut_annuel} €/an",

        # cohérence temps de travail
        "salarié . contrat . temps de travail . temps partiel": temps_partiel,
        "salarié . contrat . temps de travail . quotité": f"{quotite*100:.4f} %",

        # (optionnel mais stabilise un peu) : scénario standard
        "salarié . contrat . statut cadre": "non",
    }
    
    # Ajouter la configuration de l'impôt selon le mode choisi
    if not USE_IMPOT_AUTO:
        # Mode taux personnalisé
        situation["impôt . méthode de calcul . taux personnalisé"] = "oui"
        situation["impôt . taux personnalisé"] = f"{TAUX_IMPOT_PERSO} %"
    else:
        # Mode calcul automatique: on utilise le barème progressif réel
        # Par défaut, l'API calcule avec 1 part fiscale (célibataire)
        # Vous pouvez ajuster ces paramètres si nécessaire:
        # situation["impôt . méthode de calcul"] = "barème standard"
        # situation["foyer fiscal . nombre de parts"] = "1"
        # L'API devrait calculer automatiquement avec le barème progressif
        pass
    
    return situation

def eval_salaire(brut_annuel):
    payload = {
        "expressions": EXPRESSIONS,
        "situation": build_situation(brut_annuel)
    }

    data = call_api(payload)
    evs = data["evaluate"]  # ordre identique à EXPRESSIONS

    vals = []
    units = []
    for item in evs:
        vals.append(item.get("nodeValue"))
        units.append(item.get("unit"))

    vals = [to_annual(v, u) for v, u in zip(vals, units)]

    # Récupération des valeurs de l'API
    cout_total_employeur = vals[0]
    salaire_brut = vals[1]
    salaire_net = vals[2]
    salaire_net_apres_impot_api = vals[3]
    montant_impot_api = vals[4] if len(vals) > 4 else None
    
    # Calcul de l'impôt manuellement si l'API ne le calcule pas
    # On utilise le salaire net comme base de calcul (revenu imposable)
    if montant_impot_api is None or montant_impot_api == 0:
        # Calcul manuel de l'impôt avec le barème progressif
        montant_impot = calculer_impot_revenu(salaire_net, nombre_parts=NOMBRE_PARTS_FISCALES)
        # Recalcul du supernet avec l'impôt calculé
        salaire_net_apres_impot = salaire_net - montant_impot
    else:
        # L'API a calculé l'impôt, on utilise ses valeurs
        montant_impot = montant_impot_api
        salaire_net_apres_impot = salaire_net_apres_impot_api

    return {
        "cout_total_employeur": cout_total_employeur,
        "salaire_brut": salaire_brut,
        "salaire_net": salaire_net,
        "salaire_net_apres_impot": salaire_net_apres_impot,
        "montant_impot": montant_impot,
    }

out_path = BASE_DIR / "mon_entreprise_grille_salaires.csv"
rows = []
start = 1000

# reprise si fichier existe
if out_path.exists():
    old = pd.read_csv(out_path)
    rows = old.to_dict("records")
    if len(rows):
        start = int(rows[-1]["salaire_brut"]) + 1000

for brut in range(start, 500000 + 1000, 1000):
    rows.append(eval_salaire(brut))

    # flush chaque ligne (safe si tu interromps)
    pd.DataFrame(rows).to_csv(out_path, index=False)

    # throttle doux pour éviter les 429
    time.sleep(0.25)

print("OK ->", out_path)
