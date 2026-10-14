"""
Experimentos de la Parte 1.

1) Correctitud: en 300 instancias pequeñas, el voraz debe igualar al exacto (DP).
2) Tiempos: se varía N con B fijo y B con N fijo, se mide el tiempo real
   (mediana de varias repeticiones) y se compara contra T(N,B) = N + B log2 N.
   Si la teoría es correcta, tiempo / (N + B log2 N) debe quedar casi constante.

Uso:  python experimentos_parte1.py
"""
import csv
import math
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from instancias import instancia_reparto
from parte1_reparto import voraz_heap, exacto_dp, voraz_heap_contando

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
os.makedirs(SALIDA, exist_ok=True)


def verificar_correctitud(casos=300):
    fallos = 0
    for s in range(casos):
        N = 2 + s % 6           # N entre 2 y 7
        B = 1 + (s * 7) % 25    # B entre 1 y 25
        us, B = instancia_reparto(N, B, semilla=s)
        _, v_voraz = voraz_heap(us, B)
        _, v_exacto = exacto_dp(us, B)
        if abs(v_voraz - v_exacto) > 1e-9:
            fallos += 1
            print(f"  FALLO semilla={s}: voraz={v_voraz} exacto={v_exacto}")
    print(f"Correctitud: {casos - fallos}/{casos} instancias con voraz == óptimo")
    return fallos == 0


def medir(N, B, reps=5):
    us, B = instancia_reparto(N, B, semilla=N * 1000 + B)
    tiempos = []
    for _ in range(reps):
        t0 = time.perf_counter()
        voraz_heap(us, B)
        tiempos.append(time.perf_counter() - t0)
    return statistics.median(tiempos)


def teoria(N, B):
    return N + B * math.log2(max(N, 2))


def barrido(nombre, pares):
    filas = []
    for N, B in pares:
        t = medir(N, B)
        filas.append({"N": N, "B": B, "tiempo_s": t, "teoria": teoria(N, B),
                      "ratio": t / teoria(N, B)})
        print(f"  N={N:>7}  B={B:>8}  t={t*1e3:9.2f} ms  t/(N+B log N)={filas[-1]['ratio']:.3e}")
    with open(os.path.join(SALIDA, f"parte1_{nombre}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)
    return filas


def ajustar_constantes(filas):
    """
    O(N + B log N) esconde DOS constantes distintas: t ≈ c1*N + c2*B*log2(N).
    c1 = costo por nodo al construir el heap; c2 = costo por paso del heap.
    Se estiman por mínimos cuadrados (sin intercepto) con todas las mediciones.
    """
    import numpy as np
    A = np.array([[r["N"], r["B"] * math.log2(r["N"])] for r in filas])
    t = np.array([r["tiempo_s"] for r in filas])
    (c1, c2), *_ = np.linalg.lstsq(A, t, rcond=None)
    pred = A @ np.array([c1, c2])
    r2 = 1 - ((t - pred) ** 2).sum() / ((t - t.mean()) ** 2).sum()
    return c1, c2, r2


def graficar(filas, eje, titulo, archivo, c1, c2):
    xs = [r[eje] for r in filas]
    ts = [r["tiempo_s"] * 1e3 for r in filas]
    teo = [(c1 * r["N"] + c2 * r["B"] * math.log2(r["N"])) * 1e3 for r in filas]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.plot(xs, ts, "o-", label="medido")
    a1.plot(xs, teo, "--", label=r"$c_1 N + c_2 B\log_2 N$ (ajuste)")
    a1.set_xlabel(eje); a1.set_ylabel("tiempo (ms)"); a1.set_title(titulo)
    if eje == "N":
        a1.set_xscale("log", base=2); a2.set_xscale("log", base=2)
    a1.legend(); a1.grid(alpha=.3)
    a2.plot(xs, [m / p for m, p in zip(ts, teo)], "o-")
    a2.axhline(1, color="gray", lw=.8)
    a2.set_xlabel(eje); a2.set_ylabel("medido / predicho")
    a2.set_title("Cociente (≈ 1 si la teoría es correcta)")
    a2.set_ylim(0, 2); a2.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, archivo), dpi=130)
    plt.close(fig)


def conteo_operaciones():
    """
    Cuenta comparaciones reales del heap y las compara con las cotas teóricas:
      heapify:  <= 2N comparaciones
      cada paso (heapreplace): <= 2*log2(N) comparaciones  -> total <= 2 B log2 N
    """
    filas = []
    for N in (2**k for k in range(6, 19, 2)):         # 64 ... 262 144
        B = 20 * N
        us, _ = instancia_reparto(N, B, semilla=N)
        ch, cp = voraz_heap_contando(us, B)
        filas.append({"N": N, "B": B, "cmp_heapify": ch, "cmp_pasos": cp,
                      "heapify/N": ch / N, "pasos/(B log2 N)": cp / (B * math.log2(N))})
        print(f"  N={N:>7}  B={B:>8}  heapify: {ch/N:.2f}·N   pasos: {cp/(B*math.log2(N)):.2f}·B·log2N")
    with open(os.path.join(SALIDA, "parte1_conteo.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot([r["N"] for r in filas], [r["heapify/N"] for r in filas], "o-", label="comparaciones heapify / N")
    ax.plot([r["N"] for r in filas], [r["pasos/(B log2 N)"] for r in filas], "s-", label=r"comparaciones pasos / $(B\log_2 N)$")
    ax.axhline(2, color="gray", ls="--", lw=.8, label="cota teórica = 2")
    ax.set_xscale("log", base=2); ax.set_ylim(0, 2.5); ax.set_xlabel("N (B = 20N)")
    ax.set_title("Conteo de operaciones vs. cota teórica"); ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "parte1_conteo.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    verificar_correctitud()

    print("\nBarrido 1: B fijo = 200 000, N creciente")
    f1 = barrido("variaN", [(N, 200_000) for N in (1_000, 4_000, 16_000, 64_000, 256_000, 1_024_000)])

    print("\nBarrido 2: N fijo = 10 000, B creciente")
    f2 = barrido("variaB", [(10_000, B) for B in (50_000, 100_000, 200_000, 400_000, 800_000, 1_600_000)])

    c1, c2, r2 = ajustar_constantes(f1 + f2)
    print(f"\nAjuste t = c1*N + c2*B*log2(N):  c1 = {c1:.2e} s/nodo,  c2 = {c2:.2e} s/paso,  R² = {r2:.4f}")
    graficar(f1, "N", "Variando N (B = 200 000)", "parte1_variaN.png", c1, c2)
    graficar(f2, "B", "Variando B (N = 10 000)", "parte1_variaB.png", c1, c2)

    print("\nConteo de comparaciones del montículo (independiente de la máquina)")
    conteo_operaciones()
    print(f"\nGráficas y CSV en {SALIDA}")
