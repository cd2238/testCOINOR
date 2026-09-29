"""Comparaison de plusieurs solveurs sur un ou plusieurs problèmes."""
from __future__ import annotations

import statistics

import matplotlib.pyplot as plt

from .probleme import Probleme, Resultat
from .solveurs import Solveur


class Comparateur:
    def __init__(self, solveurs: list[Solveur]):
        self.solveurs = solveurs

    def comparer(self, pb: Probleme) -> list[Resultat]:
        """Résout pb avec chaque solveur compatible et vérifie la cohérence."""
        resultats = []
        for s in self.solveurs:
            if not s.supporte(pb):
                continue
            r = s.resoudre(pb)
            if not r.optimal:
                print(f"  attention : {r.solveur} n'a pas prouvé l'optimalité (n={pb.n})")
            resultats.append(r)

        entiers = [r for r in resultats if r.entier and r.optimal]
        if entiers and any(abs(r.objectif - entiers[0].objectif) > 1e-6 for r in entiers):
            print(f"  attention : objectifs entiers différents (n={pb.n}) : "
                  + ", ".join(f"{r.solveur}={r.objectif:.2f}" for r in entiers))
        return resultats

    @staticmethod
    def afficher(pb: Probleme, resultats: list[Resultat]) -> None:
        print(f"{'Méthode':<20}{'Solution':<38}{'Profit':>10}{'Temps (s)':>12}")
        print("-" * 80)
        for r in resultats:
            sol = ", ".join(f"{pb.nom(i)}={v:.2f}" for i, v in enumerate(r.valeurs))
            print(f"{r.solveur:<20}{sol:<38}{r.objectif:>10.2f}{r.duree:>12.4f}")

    def etude_taille(self, tailles: list[int], essais: int = 3) -> None:
        """Temps médian par solveur et écart de la relaxation, selon la taille."""
        temps: dict[str, dict[int, float]] = {}
        ecarts: dict[int, float] = {}

        for n in tailles:
            durees: dict[str, list[float]] = {}
            gaps: list[float] = []
            for essai in range(essais):
                pb = Probleme.aleatoire(n, seed=essai)
                resultats = self.comparer(pb)
                for r in resultats:
                    durees.setdefault(r.solveur, []).append(r.duree)
                ref = next((r for r in resultats if r.entier and r.optimal), None)
                relax = next((r for r in resultats if not r.entier), None)
                if ref and relax:
                    gaps.append(100 * (relax.objectif - ref.objectif) / ref.objectif)
            for nom, liste in durees.items():
                temps.setdefault(nom, {})[n] = statistics.median(liste)
            if gaps:
                ecarts[n] = statistics.median(gaps)
            print(f"n = {n:4d} : " + " | ".join(
                f"{nom} {temps[nom][n]:.3f}s" for nom in temps if n in temps[nom]))

        self._tracer(temps, ecarts)

    @staticmethod
    def _tracer(temps, ecarts) -> None:
        fig, axes = plt.subplots(1, 2 if ecarts else 1, figsize=(13 if ecarts else 7, 5))
        ax1 = axes[0] if ecarts else axes

        for nom, serie in temps.items():
            ns = sorted(serie)
            ax1.plot(ns, [serie[n] for n in ns], marker="o", label=nom)
        ax1.set_xlabel("Taille (nombre de variables)")
        ax1.set_ylabel("Temps de résolution (s)")
        ax1.set_yscale("log")
        ax1.set_title("Temps de calcul")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        if ecarts:
            ns = sorted(ecarts)
            axes[1].plot(ns, [ecarts[n] for n in ns], marker="o", color="tab:red")
            axes[1].set_xlabel("Taille (nombre de variables)")
            axes[1].set_ylabel("Écart borne LP / optimum entier (%)")
            axes[1].set_title("Qualité de la relaxation continue")
            axes[1].grid(True, alpha=0.3)


        plt.savefig("img/comp.png")
        #plt.tight_layout()
        #plt.show()
