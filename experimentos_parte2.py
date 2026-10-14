"""
Experimentos de la Parte 2.

1) Sanidad: la cobertura ponderada es monótona y submodular (prueba aleatoria).
2) Cota (1 - 1/e): en 500 instancias pequeñas se compara voraz vs. óptimo
   (fuerza bruta) y se verifica que voraz/óptimo >= 1 - 1/e ≈ 0.632.
3) Tiempos del voraz: variando N (k fijo) y k (N fijo); se compara contra
   T(N,k) = N·k·d. Además se cuentan las evaluaciones de ganancia marginal,
   que deben ser exactamente kN - k(k-1)/2.
4) Voraz vs. fuerza bruta: tiempo al crecer k (escala logarítmica),
   para mostrar el crecimiento exponencial C(N,k) del exacto.

Uso:  python experimentos_parte2.py
"""
import csv
import math
import os
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from instancias import instancia_cobertura
from parte2_seleccion import f, voraz_submodular, fuerza_bruta

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
os.makedirs(SALIDA, exist_ok=True)
COTA = 1 - 1 / math.e


def guardar_csv(nombre, filas):
    with open(os.path.join(SALIDA, nombre), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)


# 1) -------------------------------------------------------------------------
def sanidad_submodular(pruebas=2000, semilla=1):
    rng = random.Random(semilla)
    conjuntos, pesos = instancia_cobertura(12, 30, 6, semilla=semilla)
    violaciones = 0
    for _ in range(pruebas):
        A2 = set(rng.sample(range(12), rng.randint(0, 11)))   # A'
        A = set(x for x in A2 if rng.random() < 0.5)            # A ⊆ A'
        resto = [v for v in range(12) if v not in A2]
        if not resto:
            continue
        v = rng.choice(resto)
        fA, fA2 = f(A, conjuntos, pesos), f(A2, conjuntos, pesos)
        mono = fA <= fA2 + 1e-9
        sub = (f(A | {v}, conjuntos, pesos) - fA) >= (f(A2 | {v}, conjuntos, pesos) - fA2) - 1e-9
        violaciones += (not mono) + (not sub)
    print(f"Sanidad: {pruebas} pruebas aleatorias de monotonía y submodularidad -> {violaciones} violaciones")


# 2) -------------------------------------------------------------------------
def instancia_dificil(N, M, semilla):
    """Universo pequeño y tamaños variables: mucho traslape, donde el voraz más se equivoca."""
    rng = random.Random(semilla)
    pesos = [rng.uniform(1, 10) for _ in range(M)]
    conjuntos = [frozenset(rng.sample(range(M), rng.randint(1, max(2, M // 3)))) for _ in range(N)]
    return conjuntos, pesos


def verificar_cota(casos=500):
    filas = []
    for s in range(casos):
        rng = random.Random(s)
        N, k, M = rng.randint(6, 14), rng.randint(2, 5), rng.randint(8, 20)
        conj, w = instancia_dificil(N, M, s)
        _, v_voraz = voraz_submodular(conj, w, k)
        _, v_opt = fuerza_bruta(conj, w, k)
        filas.append({"semilla": s, "N": N, "k": k, "M": M, "voraz": v_voraz,
                      "optimo": v_opt, "razon": v_voraz / v_opt})
    guardar_csv("parte2_cota.csv", filas)
    razones = [r["razon"] for r in filas]
    exactos = sum(r > 1 - 1e-12 for r in razones)
    print(f"Cota (1-1/e): {casos} instancias | razón mínima = {min(razones):.4f} "
          f"(cota {COTA:.4f}) | voraz óptimo en {exactos}/{casos} | "
          f"{'TODAS cumplen' if min(razones) >= COTA else 'HAY VIOLACIONES'}")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(razones, bins=np.linspace(0.6, 1.0, 41), edgecolor="white")
    ax.axvline(COTA, color="red", ls="--", label=f"cota garantizada 1−1/e ≈ {COTA:.3f}")
    ax.set_xlabel("utilidad voraz / utilidad óptima"); ax.set_ylabel("número de instancias")
    ax.set_title(f"Calidad del voraz en {casos} instancias (mínimo observado {min(razones):.3f})")
    ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "parte2_cota.png"), dpi=130); plt.close(fig)


# 3) -------------------------------------------------------------------------
def medir_voraz(N, k, M, d, reps=7):
    conj, w = instancia_cobertura(N, M, d, semilla=N * 7 + k)
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        _, _, ev = voraz_submodular(conj, w, k, contar=True)
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts), ev


def barrido_voraz(nombre, pares, M, d):
    filas = []
    for N, k in pares:
        t, ev = medir_voraz(N, k, M, d)
        esperado = k * N - k * (k - 1) // 2
        filas.append({"N": N, "k": k, "d": d, "tiempo_s": t, "evaluaciones": ev,
                      "eval_teoricas": esperado, "t/(N k d)": t / (N * k * d)})
        print(f"  N={N:>6} k={k:>4}  t={t*1e3:9.1f} ms  evaluaciones={ev:>8} "
              f"(teoría {esperado:>8})  t/(N·k·d)={t/(N*k*d):.2e}")
    guardar_csv(f"parte2_{nombre}.csv", filas)
    return filas


def graficar_voraz(filas, eje, titulo, archivo):
    xs = [r[eje] for r in filas]
    ts = [r["tiempo_s"] * 1e3 for r in filas]
    c = statistics.median(r["t/(N k d)"] for r in filas)
    teo = [c * r["N"] * r["k"] * r["d"] * 1e3 for r in filas]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.plot(xs, ts, "o-", label="medido"); a1.plot(xs, teo, "--", label=r"$c\cdot N k d$")
    a1.set_xlabel(eje); a1.set_ylabel("tiempo (ms)"); a1.set_title(titulo); a1.legend(); a1.grid(alpha=.3)
    a2.plot(xs, [r["t/(N k d)"] / c for r in filas], "o-"); a2.axhline(1, color="gray", lw=.8)
    a2.set_ylim(0, 2); a2.set_xlabel(eje); a2.set_ylabel("medido / predicho")
    a2.set_title("Cociente (≈ 1 si la teoría es correcta)"); a2.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, archivo), dpi=130); plt.close(fig)


# 4) -------------------------------------------------------------------------
def voraz_vs_fuerza_bruta(M=60, d=6):
    """Crecen N y k = N/2 a la vez: C(N, N/2) ~ 2^N / sqrt(N), crecimiento exponencial."""
    filas = []
    for N in range(8, 23, 2):
        k = N // 2
        conj, w = instancia_cobertura(N, M, d, semilla=N)
        t0 = time.perf_counter(); _, vv = voraz_submodular(conj, w, k); tv = time.perf_counter() - t0
        t0 = time.perf_counter(); _, vo = fuerza_bruta(conj, w, k); tb = time.perf_counter() - t0
        filas.append({"N": N, "k": k, "C(N,k)": math.comb(N, k), "t_voraz_s": tv,
                      "t_fuerza_bruta_s": tb, "razon": vv / vo})
        print(f"  N={N:>2} k={k:>2}  C(N,k)={math.comb(N,k):>7}  voraz={tv*1e3:7.3f} ms  "
              f"fuerza bruta={tb*1e3:9.1f} ms  voraz/óptimo={vv/vo:.3f}")
    guardar_csv("parte2_voraz_vs_fb.csv", filas)
    fig, ax = plt.subplots(figsize=(7, 4))
    Ns = [r["N"] for r in filas]
    ax.semilogy(Ns, [r["t_fuerza_bruta_s"] * 1e3 for r in filas], "s-", label="fuerza bruta  O(C(N,k)·k·d)")
    ax.semilogy(Ns, [r["t_voraz_s"] * 1e3 for r in filas], "o-", label="voraz  O(N·k·d)")
    ax.set_xlabel("N  (con k = N/2)"); ax.set_ylabel("tiempo (ms, escala log)")
    ax.set_title("Exacto exponencial vs. aproximación polinomial"); ax.legend(); ax.grid(alpha=.3, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "parte2_voraz_vs_fb.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    sanidad_submodular()
    print()
    verificar_cota()

    M, d = 2000, 20
    print(f"\nVoraz, k fijo = 20, N creciente (M={M}, d={d})")
    f1 = barrido_voraz("variaN", [(N, 20) for N in (500, 1000, 2000, 4000, 8000, 16000)], M, d)
    graficar_voraz(f1, "N", "Voraz: variando N (k = 20)", "parte2_variaN.png")
    print(f"\nVoraz, N fijo = 2000, k creciente")
    f2 = barrido_voraz("variak", [(2000, k) for k in (10, 20, 40, 80, 160, 320)], M, d)
    graficar_voraz(f2, "k", "Voraz: variando k (N = 2000)", "parte2_variak.png")

    print("\nVoraz vs. fuerza bruta (k = N/2)")
    voraz_vs_fuerza_bruta()
    print(f"\nGráficas y CSV en {SALIDA}")
