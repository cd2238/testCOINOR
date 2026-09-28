"""Données du problème et format de résultat commun à tous les solveurs."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Probleme:
    """max profit·x  sous  conso·x <= capacite,  x >= 0.

    conso[j][i] = consommation de la ressource j par la variable i.
    Les coefficients doivent être entiers pour CP-SAT et l'énumération.
    """
    profit: list[int]
    conso: list[list[int]]
    capacite: list[int]
    noms: tuple[str, ...] | None = None

    @property
    def n(self) -> int:
        return len(self.profit)

    @property
    def m(self) -> int:
        return len(self.capacite)

    def nom(self, i: int) -> str:
        return self.noms[i] if self.noms else f"x_{i}"

    def bornes(self) -> list[int]:
        """Borne haute de chaque variable, déduite des contraintes."""
        return [
            min(self.capacite[j] // self.conso[j][i]
                for j in range(self.m) if self.conso[j][i] > 0)
            for i in range(self.n)
        ]

    @classmethod
    def aleatoire(cls, n: int, seed: int) -> Probleme:
        """n variables, n // 2 ressources, coefficients aléatoires."""
        rng = random.Random(seed)
        m = max(1, n // 2)
        profit = [rng.randint(10, 50) for _ in range(n)]
        conso = [[rng.randint(1, 10) for _ in range(n)] for _ in range(m)]
        capacite = [sum(ligne) * 3 for ligne in conso]
        return cls(profit, conso, capacite)


@dataclass
class Resultat:
    solveur: str
    valeurs: list[float]
    objectif: float
    duree: float
    optimal: bool
    entier: bool
