"""
Experimentos de la Parte 2 (monotonía, submodularidad y la reducción se prueban
en tests/test_parte2.py).

1) Cota (1 - 1/e): en 500 instancias pequeñas se compara voraz vs. óptimo
   (fuerza bruta) y se verifica que voraz/óptimo >= 1 - 1/e ≈ 0.632.
2) Tiempos del voraz: variando N (k fijo) y k (N fijo); se compara contra
   T(N,k) = N·k·d. Además se cuentan las evaluaciones de ganancia marginal,
   que deben ser exactamente kN - k(k-1)/2.
3) Voraz vs. fuerza bruta: tiempo al crecer k (escala logarítmica),
   para mostrar el crecimiento exponencial C(N,k) del exacto.

Uso:  python -m experimentos.parte2
"""
import math
import os
import random
import statistics
import time

import matplotlib.pyplot as plt
import numpy as np

from ada.generadores import instancia_cobertura, instancia_cobertura_dificil
from ada.parte2 import fuerza_bruta, voraz_submodular
from experimentos.comun import carpeta_salida, grafica_medido_vs_teoria, guardar_csv, medir_mediana

SALIDA = carpeta_salida("parte2")
COTA = 1 - 1 / math.e


# 1) -------------------------------------------------------------------------
def verificar_cota(casos=500):
    filas = []
    for s in range(casos):
        rng = random.Random(s)
        N, k, M = rng.randint(6, 14), rng.randint(2, 5), rng.randint(8, 20)
        inst = instancia_cobertura_dificil(N, M, s)
        _, v_voraz = voraz_submodular(inst.conjuntos, inst.pesos, k)
        _, v_opt = fuerza_bruta(inst.conjuntos, inst.pesos, k)
        filas.append({"semilla": s, "N": N, "k": k, "M": M, "voraz": v_voraz,
                      "optimo": v_opt, "razon": v_voraz / v_opt})
    guardar_csv(os.path.join(SALIDA, "cota.csv"), filas)
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
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "cota.png"), dpi=130); plt.close(fig)


# 2) -------------------------------------------------------------------------
def barrido_voraz(nombre, pares, M, d):
    filas = []
    for N, k in pares:
        inst = instancia_cobertura(N, M, d, semilla=N * 7 + k)
        t = medir_mediana(lambda: voraz_submodular(inst.conjuntos, inst.pesos, k), reps=7)
        _, _, ev = voraz_submodular(inst.conjuntos, inst.pesos, k, contar=True)
        esperado = k * N - k * (k - 1) // 2
        filas.append({"N": N, "k": k, "d": d, "tiempo_s": t, "evaluaciones": ev,
                      "eval_teoricas": esperado, "t/(N k d)": t / (N * k * d)})
        print(f"  N={N:>6} k={k:>4}  t={t*1e3:9.1f} ms  evaluaciones={ev:>8} "
              f"(teoría {esperado:>8})  t/(N·k·d)={t/(N*k*d):.2e}")
    guardar_csv(os.path.join(SALIDA, f"{nombre}.csv"), filas)
    return filas


def graficar_voraz(filas, eje, titulo, archivo):
    c = statistics.median(r["t/(N k d)"] for r in filas)
    grafica_medido_vs_teoria(
        xs=[r[eje] for r in filas],
        medido_ms=[r["tiempo_s"] * 1e3 for r in filas],
        teoria_ms=[c * r["N"] * r["k"] * r["d"] * 1e3 for r in filas],
        eje=eje, titulo=titulo, etiqueta_teoria=r"$c\cdot N k d$",
        ruta=os.path.join(SALIDA, archivo))


# 3) -------------------------------------------------------------------------
def voraz_vs_fuerza_bruta(M=60, d=6):
    """Crecen N y k = N/2 a la vez: C(N, N/2) ~ 2^N / sqrt(N), crecimiento exponencial."""
    filas = []
    for N in range(8, 23, 2):
        k = N // 2
        inst = instancia_cobertura(N, M, d, semilla=N)
        t0 = time.perf_counter(); _, vv = voraz_submodular(inst.conjuntos, inst.pesos, k); tv = time.perf_counter() - t0
        t0 = time.perf_counter(); _, vo = fuerza_bruta(inst.conjuntos, inst.pesos, k); tb = time.perf_counter() - t0
        filas.append({"N": N, "k": k, "C(N,k)": math.comb(N, k), "t_voraz_s": tv,
                      "t_fuerza_bruta_s": tb, "razon": vv / vo})
        print(f"  N={N:>2} k={k:>2}  C(N,k)={math.comb(N,k):>7}  voraz={tv*1e3:7.3f} ms  "
              f"fuerza bruta={tb*1e3:9.1f} ms  voraz/óptimo={vv/vo:.3f}")
    guardar_csv(os.path.join(SALIDA, "voraz_vs_fb.csv"), filas)
    fig, ax = plt.subplots(figsize=(7, 4))
    Ns = [r["N"] for r in filas]
    ax.semilogy(Ns, [r["t_fuerza_bruta_s"] * 1e3 for r in filas], "s-", label="fuerza bruta  O(C(N,k)·k·d)")
    ax.semilogy(Ns, [r["t_voraz_s"] * 1e3 for r in filas], "o-", label="voraz  O(N·k·d)")
    ax.set_xlabel("N  (con k = N/2)"); ax.set_ylabel("tiempo (ms, escala log)")
    ax.set_title("Exacto exponencial vs. aproximación polinomial"); ax.legend(); ax.grid(alpha=.3, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "voraz_vs_fb.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    verificar_cota()

    M, d = 2000, 20
    print(f"\nVoraz, k fijo = 20, N creciente (M={M}, d={d})")
    f1 = barrido_voraz("variaN", [(N, 20) for N in (500, 1000, 2000, 4000, 8000, 16000)], M, d)
    graficar_voraz(f1, "N", "Voraz: variando N (k = 20)", "variaN.png")
    print(f"\nVoraz, N fijo = 2000, k creciente")
    f2 = barrido_voraz("variak", [(2000, k) for k in (10, 20, 40, 80, 160, 320)], M, d)
    graficar_voraz(f2, "k", "Voraz: variando k (N = 2000)", "variak.png")

    print("\nVoraz vs. fuerza bruta (k = N/2)")
    voraz_vs_fuerza_bruta()
    print(f"\nGráficas y CSV en {SALIDA}")
