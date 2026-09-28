"""Point d'entrée : python main.py"""
from .comparateur import Comparateur
from .probleme import Probleme
from .solveurs import SolveurCBC, SolveurCPSAT, SolveurEnumeration


def main() -> None:
    comparateur = Comparateur([
        SolveurCBC(),
        SolveurCBC(relaxation=True),
        SolveurCPSAT(),
        SolveurEnumeration(),
    ])

    # 1) Le problème tables et chaises
    pb = Probleme(
        profit=[40, 30],
        conso=[[2, 1], [1, 1]],
        capacite=[100, 80],
        noms=("tables", "chaises"),
    )
    Comparateur.afficher(pb, comparateur.comparer(pb))

    # 2) Étude selon la taille (l'énumération est ignorée dès que l'espace est trop grand)
    comparateur.etude_taille([10, 20, 50])


if __name__ == "__main__":
    main()
