"""Solveurs : une classe abstraite et une sous-classe par méthode."""
from __future__ import annotations

import itertools
import time
from abc import ABC, abstractmethod

import pulp
from ortools.sat.python import cp_model

from .probleme import Probleme, Resultat


class Solveur(ABC):
    entier = True  # False pour une relaxation continue

    @property
    @abstractmethod
    def nom(self) -> str: ...

    def supporte(self, pb: Probleme) -> bool:
        return True

    @abstractmethod
    def resoudre(self, pb: Probleme) -> Resultat: ...


class SolveurCBC(Solveur):
    """CBC via PuLP 4 (COIN_CMD). Nécessite l'exécutable cbc installé."""

    def __init__(self, relaxation: bool = False):
        self.relaxation = relaxation
        self.entier = not relaxation

    @property
    def nom(self) -> str:
        return "CBC (relaxation)" if self.relaxation else "CBC (entier)"

    def resoudre(self, pb: Probleme) -> Resultat:
        cat = "Continuous" if self.relaxation else "Integer"
        prob = pulp.LpProblem("Production", pulp.LpMaximize)
        x = [prob.add_variable(pb.nom(i), 0, None, cat=cat) for i in range(pb.n)]
        prob += pulp.lpSum(pb.profit[i] * x[i] for i in range(pb.n)), "Profit"
        for j in range(pb.m):
            prob += (pulp.lpSum(pb.conso[j][i] * x[i] for i in range(pb.n))
                     <= pb.capacite[j]), f"Ressource_{j}"

        debut = time.perf_counter()
        stats = prob.solve(pulp.COIN_CMD(msg=False))
        duree = time.perf_counter() - debut

        return Resultat(
            self.nom,
            [pulp.value(v) for v in x],
            pulp.value(prob.objective),
            duree,
            stats.status_str == "Optimal",
            self.entier,
        )


class SolveurCPSAT(Solveur):
    """CP-SAT d'OR-Tools (variables entières bornées, coefficients entiers)."""

    def __init__(self, limite: float = 60):
        self.limite = limite

    @property
    def nom(self) -> str:
        return "CP-SAT"

    def resoudre(self, pb: Probleme) -> Resultat:
        model = cp_model.CpModel()
        bornes = pb.bornes()
        x = [model.new_int_var(0, bornes[i], pb.nom(i)) for i in range(pb.n)]
        for j in range(pb.m):
            model.add(sum(int(pb.conso[j][i]) * x[i] for i in range(pb.n))
                      <= int(pb.capacite[j]))
        model.maximize(sum(int(pb.profit[i]) * x[i] for i in range(pb.n)))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.limite

        debut = time.perf_counter()
        statut = solver.solve(model)
        duree = time.perf_counter() - debut

        return Resultat(
            self.nom,
            [solver.value(v) for v in x],
            solver.objective_value,
            duree,
            statut == cp_model.OPTIMAL,
            True,
        )


class SolveurEnumeration(Solveur):
    """Teste toutes les combinaisons entières : réservé aux petits problèmes."""

    def __init__(self, max_combinaisons: int = 5_000_000):
        self.max_combinaisons = max_combinaisons

    @property
    def nom(self) -> str:
        return "Énumération"

    def supporte(self, pb: Probleme) -> bool:
        total = 1
        for b in pb.bornes():
            total *= b + 1
            if total > self.max_combinaisons:
                return False
        return True

    def resoudre(self, pb: Probleme) -> Resultat:
        debut = time.perf_counter()
        meilleur, meilleur_obj = None, float("-inf")
        for x in itertools.product(*(range(b + 1) for b in pb.bornes())):
            if all(sum(pb.conso[j][i] * x[i] for i in range(pb.n)) <= pb.capacite[j]
                   for j in range(pb.m)):
                obj = sum(pb.profit[i] * x[i] for i in range(pb.n))
                if obj > meilleur_obj:
                    meilleur, meilleur_obj = x, obj
        duree = time.perf_counter() - debut
        return Resultat(self.nom, list(meilleur), meilleur_obj, duree, True, True)
