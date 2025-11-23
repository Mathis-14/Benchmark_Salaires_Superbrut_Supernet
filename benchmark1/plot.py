import matplotlib
matplotlib.use("Agg")  # backend non-interactif (pas de fenêtres Mac)

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ====== CONFIG ======
# Définir le répertoire de base comme étant le répertoire du script (benchmark1)
BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "mon_entreprise_grille_salaires.csv"
OUT_DIR = BASE_DIR / "graphs"
DPI = 200
# ====================

def savefig(path: Path):
    plt.tight_layout()
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print("saved ->", path)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_PATH).sort_values("salaire_brut")
    df = df[(df["salaire_brut"] > 0) & (df["cout_total_employeur"] > 0)]
    
    # Calcul de l'impôt si la colonne existe, sinon on l'estime
    if "montant_impot" in df.columns:
        df["impot_calcule"] = df["montant_impot"]
    else:
        # Estimation: différence entre net avant et après impôt
        df["impot_calcule"] = df["salaire_net"] - df["salaire_net_apres_impot"]
    
    # Vérification de cohérence
    df["difference_net"] = df["salaire_net"] - df["salaire_net_apres_impot"]
    if (df["difference_net"].abs() < 1).all():
        print("⚠️  ATTENTION: L'impôt ne semble pas être calculé (net ≈ net après impôt)")
        print("   Vérifiez que le script utilise le calcul automatique de l'impôt")
    
    # ====== 1) Taux net effectif (net / brut) ======
    df["taux_net_sur_brut"] = df["salaire_net"] / df["salaire_brut"]

    plt.figure(figsize=(10, 6))
    plt.plot(df["salaire_brut"], df["taux_net_sur_brut"], linewidth=2)
    plt.title("Taux net effectif (net / brut)", fontsize=14, fontweight="bold")
    plt.xlabel("Salaire brut annuel (€)")
    plt.ylabel("Net / Brut")
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    savefig(OUT_DIR / "taux_net_effectif_net_sur_brut.png")
    plt.close()

    # ====== 2) Taux supernet effectif (supernet / superbrut) ======
    df["taux_supernet_sur_superbrut"] = (
        df["salaire_net_apres_impot"] / df["cout_total_employeur"]
    )

    plt.figure(figsize=(10, 6))
    plt.plot(df["cout_total_employeur"], df["taux_supernet_sur_superbrut"], linewidth=2, color="green")
    plt.title("Taux supernet effectif (supernet / superbrut)", fontsize=14, fontweight="bold")
    plt.xlabel("Coût total employeur annuel (€) (superbrut)")
    plt.ylabel("Supernet / Superbrut")
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    savefig(OUT_DIR / "taux_supernet_effectif_supernet_sur_superbrut.png")
    plt.close()

    # ====== 3) Superbrut -> Supernet RECONSTRUIT via le taux effectif ======
    df["supernet_reconstruit"] = df["taux_supernet_sur_superbrut"] * df["cout_total_employeur"]

    plt.figure(figsize=(10, 6))
    plt.plot(df["cout_total_employeur"], df["supernet_reconstruit"], 
             label="Supernet reconstruit (taux×superbrut)", linewidth=2)
    plt.plot(df["cout_total_employeur"], df["salaire_net_apres_impot"], 
             linestyle="--", label="Supernet CSV (direct)", linewidth=2, alpha=0.7)
    plt.title("Supernet en fonction du superbrut (reconstruit via taux effectif)", 
              fontsize=14, fontweight="bold")
    plt.xlabel("Coût total employeur annuel (€) (superbrut)")
    plt.ylabel("Salaire net après impôt annuel (€) (supernet)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    savefig(OUT_DIR / "superbrut_vers_supernet_reconstruit.png")
    plt.close()
    
    # ====== 4) NOUVEAU: Comparaison Brut vs Superbrut ======
    plt.figure(figsize=(10, 6))
    plt.plot(df["salaire_brut"], df["salaire_brut"], label="Salaire brut", 
             linewidth=2, linestyle="--", alpha=0.5)
    plt.plot(df["salaire_brut"], df["cout_total_employeur"], label="Coût total employeur (superbrut)", 
             linewidth=2)
    plt.title("Comparaison: Salaire brut vs Coût total employeur", fontsize=14, fontweight="bold")
    plt.xlabel("Salaire brut annuel (€)")
    plt.ylabel("Montant annuel (€)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    savefig(OUT_DIR / "brut_vs_superbrut.png")
    plt.close()
    
    # ====== 5) NOUVEAU: Impact de l'impôt (Net avant vs après impôt) ======
    plt.figure(figsize=(10, 6))
    plt.plot(df["salaire_brut"], df["salaire_net"], label="Net avant impôt", 
             linewidth=2, color="blue")
    plt.plot(df["salaire_brut"], df["salaire_net_apres_impot"], label="Net après impôt (supernet)", 
             linewidth=2, color="red")
    if df["impot_calcule"].sum() > 0:
        plt.fill_between(df["salaire_brut"], df["salaire_net_apres_impot"], df["salaire_net"], 
                         alpha=0.3, color="orange", label="Impôt sur le revenu")
    plt.title("Impact de l'impôt sur le revenu", fontsize=14, fontweight="bold")
    plt.xlabel("Salaire brut annuel (€)")
    plt.ylabel("Salaire net annuel (€)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    savefig(OUT_DIR / "impact_impot.png")
    plt.close()
    
    # ====== 6) NOUVEAU: Taux d'imposition effectif ======
    if df["impot_calcule"].sum() > 0:
        df["taux_imposition"] = (df["impot_calcule"] / df["salaire_net"]) * 100
        plt.figure(figsize=(10, 6))
        plt.plot(df["salaire_brut"], df["taux_imposition"], linewidth=2, color="purple")
        plt.title("Taux d'imposition effectif (impôt / net avant impôt)", fontsize=14, fontweight="bold")
        plt.xlabel("Salaire brut annuel (€)")
        plt.ylabel("Taux d'imposition (%)")
        plt.grid(True, alpha=0.3)
        savefig(OUT_DIR / "taux_imposition.png")
        plt.close()
    
    # ====== 7) NOUVEAU: Comparaison Brut vs Supernet ======
    plt.figure(figsize=(10, 6))
    plt.plot(df["salaire_brut"], df["salaire_brut"], label="Salaire brut", 
             linewidth=2, linestyle="--", alpha=0.6, color="gray")
    plt.plot(df["salaire_brut"], df["salaire_net_apres_impot"], label="Supernet (net après impôt)", 
             linewidth=2, color="red")
    # Zone de différence pour visualiser l'écart
    plt.fill_between(df["salaire_brut"], df["salaire_net_apres_impot"], df["salaire_brut"], 
                     alpha=0.2, color="orange", label="Écart (cotisations + impôt)")
    plt.title("Comparaison: Salaire brut vs Supernet", fontsize=14, fontweight="bold")
    plt.xlabel("Salaire brut annuel (€)")
    plt.ylabel("Montant annuel (€)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    # Ligne de référence y=x
    max_val = max(df["salaire_brut"].max(), df["salaire_net_apres_impot"].max())
    plt.plot([0, max_val], [0, max_val], 'k--', alpha=0.2, linewidth=1)
    savefig(OUT_DIR / "brut_vs_supernet.png")
    plt.close()
    
    print(f"✅ Graphiques générés dans {OUT_DIR}/")
    print(f"   - {len(df)} points de données")
    if df["impot_calcule"].sum() > 0:
        print(f"   - Impôt calculé: OUI (max: {df['impot_calcule'].max():.2f}€)")
    else:
        print(f"   - ⚠️  Impôt calculé: NON - vérifiez la configuration")

if __name__ == "__main__":
    main()
