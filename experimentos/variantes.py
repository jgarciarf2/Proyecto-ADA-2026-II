"""
Experimentos de la variante V1 (costos de participación), docs/03_variantes.md.

1) Tiempo del algoritmo A al variar N con k = 10, contra T_A = c·N²·k.
2) Tiempo del algoritmo B al variar N con k = 5, contra T_B = c·C(N,3)·N²·k  (= O(N⁵·k)).
3) Calidad: voraz por ganancia, A y B contra el óptimo por fuerza bruta en 300 instancias
   donde el cupo no restringe (cotas ½(1 − 1/e) y 1 − 1/e) y 300 donde sí (cotas 1/k y 1/⌈k/3⌉).

Uso:  python -m experimentos.variantes      (menos de 1 minuto)
"""
import math
import os
import random
import statistics
from dataclasses import replace

import matplotlib.pyplot as plt

from ada.generadores import instancia_costos
from ada.parte2.fuerza_bruta import fuerza_bruta_general
from ada.parte2.influencia import f_influencia, voraz_influencia
from ada.variantes.costos import algoritmo_a, algoritmo_b
from experimentos.comun import carpeta_salida, grafica_medido_vs_teoria, guardar_csv, medir_mediana

SALIDA = carpeta_salida("variantes")
COTA_A, COTA_B = (1 - 1 / math.e) / 2, 1 - 1 / math.e


def barrido(nombre, algoritmo, tamanos, k, teoria, reps):
    """Mide el algoritmo en instancias de grafo completo con cupo k fijo; teoria(N, k) es la T(n) sin constante."""
    filas = []
    for N in tamanos:
        inst = replace(instancia_costos(N, semilla=N, densidad=1.0), k=k)
        t = medir_mediana(lambda: algoritmo(inst.a, inst.W, k, inst.costos, inst.P), reps=reps)
        _, _, ev = algoritmo(inst.a, inst.W, k, inst.costos, inst.P, contar=True)
        filas.append({"N": N, "k": k, "P": inst.P, "tiempo_s": t, "evaluaciones": ev, "t/teoria": t / teoria(N, k)})
        print(f"  N={N:>4} k={k:>2}  t={t * 1e3:10.2f} ms  evaluaciones={ev:>8}  t/teoría={t / teoria(N, k):.2e}")
    guardar_csv(os.path.join(SALIDA, f"{nombre}.csv"), filas)
    c = statistics.median(r["t/teoria"] for r in filas)
    return filas, c


def calidad(casos=300):
    filas = []
    for regimen in ("presupuesto", "mixto"):
        for s in range(casos):
            rng = random.Random(s)
            inst = instancia_costos(rng.randint(7, 11), semilla=s, densidad=rng.uniform(0.3, 0.9), regimen=regimen)
            _, opt = fuerza_bruta_general(lambda S: f_influencia(list(S), inst.a, inst.W), inst.k,
                                          range(inst.N), inst.costos, inst.P)
            if opt == 0:
                continue
            _, vg = voraz_influencia(inst.a, inst.W, inst.k, costos=inst.costos, presupuesto=inst.P)
            _, va = algoritmo_a(inst.a, inst.W, inst.k, inst.costos, inst.P)
            _, vb = algoritmo_b(inst.a, inst.W, inst.k, inst.costos, inst.P)
            filas.append({"regimen": regimen, "semilla": s, "N": inst.N, "k": inst.k, "P": inst.P, "optimo": opt,
                          "razon_ganancia": vg / opt, "razon_A": va / opt, "razon_B": vb / opt})
    guardar_csv(os.path.join(SALIDA, "calidad.csv"), filas)

    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    nombres = [("razon_ganancia", "Voraz por\nganancia", "#94a3b8"), ("razon_A", "Algoritmo A", "#ea7a2b"),
               ("razon_B", "Algoritmo B", "#2563eb")]
    for ax, regimen, titulo in [(ejes[0], "presupuesto", "El cupo no restringe (k ≥ kₘₐₓ(P))"),
                                (ejes[1], "mixto", "El cupo restringe (k < kₘₐₓ(P))")]:
        datos = [r for r in filas if r["regimen"] == regimen]
        for j, (col, etiqueta, color) in enumerate(nombres):
            ys = [r[col] for r in datos]
            xs = [j + random.Random(i).uniform(-0.18, 0.18) for i in range(len(ys))]
            ax.scatter(xs, ys, s=9, color=color, alpha=0.45, linewidths=0)
            ax.text(j, 0.02, f"mín. {min(ys):.3f}\nóptimo en {sum(y > 1 - 1e-9 for y in ys)}/{len(ys)}",
                    ha="center", fontsize=8, color="#1e293b")
        if regimen == "presupuesto":
            ax.axhline(COTA_A, color="#ea7a2b", ls="--", lw=1.2, label=f"cota de A: ½(1 − 1/e) ≈ {COTA_A:.3f}")
            ax.axhline(COTA_B, color="#2563eb", ls="--", lw=1.2, label=f"cota de B: 1 − 1/e ≈ {COTA_B:.3f}")
            ax.legend(frameon=False, fontsize=8, loc="center left")
        else:
            peor = min(r["razon_A"] * r["k"] for r in datos)
            ax.text(1, 0.42, f"cotas 1/k (A) y 1/⌈k/3⌉ (B), con k entre {min(r['k'] for r in datos)} y "
                             f"{max(r['k'] for r in datos)}\nmínimo de (razón de A)·k = {peor:.2f} ≥ 1",
                    ha="center", fontsize=8, color="#475569")
        ax.set_xticks(range(3), [n[1] for n in nombres], fontsize=9)
        ax.set_ylim(0, 1.05); ax.set_title(titulo, fontsize=10); ax.grid(axis="y", alpha=.3)
    ejes[0].set_ylabel("utilidad / utilidad óptima")
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "calidad.png"), dpi=150); plt.close(fig)
    for regimen in ("presupuesto", "mixto"):
        d = [r for r in filas if r["regimen"] == regimen]
        print(f"  {regimen:<11} ({len(d)} instancias): mínimo ganancia {min(r['razon_ganancia'] for r in d):.3f}, "
              f"A {min(r['razon_A'] for r in d):.3f}, B {min(r['razon_B'] for r in d):.3f}")
    return filas


if __name__ == "__main__":
    print("Algoritmo A, k = 10, N creciente (grafo completo)")
    fa, ca = barrido("tiempo_A", algoritmo_a, (50, 100, 200, 300, 400, 600), 10, lambda N, k: N * N * k, reps=5)
    grafica_medido_vs_teoria([r["N"] for r in fa], [r["tiempo_s"] * 1e3 for r in fa],
                             [ca * r["N"] ** 2 * r["k"] * 1e3 for r in fa], "N",
                             "Algoritmo A: variando N (k = 10)", r"$c\cdot N^2 k$", os.path.join(SALIDA, "tiempo_A.png"))
    print("\nAlgoritmo B, k = 5, N creciente (grafo completo)")
    teoria_b = lambda N, k: math.comb(N, 3) * N * N * k
    fb, cb = barrido("tiempo_B", algoritmo_b, (10, 14, 18, 22, 26, 30), 5, teoria_b, reps=3)
    grafica_medido_vs_teoria([r["N"] for r in fb], [r["tiempo_s"] * 1e3 for r in fb],
                             [cb * teoria_b(r["N"], r["k"]) * 1e3 for r in fb], "N",
                             "Algoritmo B: variando N (k = 5)", r"$c\cdot \binom{N}{3} N^2 k$",
                             os.path.join(SALIDA, "tiempo_B.png"))
    print("\nCalidad contra el óptimo")
    calidad()
    print(f"\nGráficas y CSV en {SALIDA}")
