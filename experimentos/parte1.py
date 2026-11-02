"""
Experimentos de la Parte 1 (la correctitud voraz == DP está en tests/test_parte1.py).

1) Tiempos: se varía N con B fijo y B con N fijo, se mide el tiempo real
   (mediana de varias repeticiones) y se compara contra T(N,B) = c1·N + c2·B log2 N.
2) Conteo de comparaciones del montículo contra las cotas teóricas 2N y 2·B·log2 N.

Uso:  python -m experimentos.parte1
"""
import math
import os

import matplotlib.pyplot as plt
import numpy as np

from ada.generadores import instancia_reparto
from ada.parte1 import ContadorComparaciones, voraz_heap
from experimentos.comun import carpeta_salida, grafica_medido_vs_teoria, guardar_csv, medir_mediana

SALIDA = carpeta_salida("parte1")


def teoria(N, B):
    return N + B * math.log2(max(N, 2))


def barrido(nombre, pares):
    filas = []
    for N, B in pares:
        inst = instancia_reparto(N, B, semilla=N * 1000 + B)
        t = medir_mediana(lambda: voraz_heap(inst.utilidades, inst.B))
        filas.append({"N": N, "B": B, "tiempo_s": t, "teoria": teoria(N, B),
                      "ratio": t / teoria(N, B)})
        print(f"  N={N:>7}  B={B:>8}  t={t*1e3:9.2f} ms  t/(N+B log N)={filas[-1]['ratio']:.3e}")
    guardar_csv(os.path.join(SALIDA, f"{nombre}.csv"), filas)
    return filas


def ajustar_constantes(filas):
    """
    O(N + B log N) esconde DOS constantes distintas: t ≈ c1*N + c2*B*log2(N).
    c1 = costo por nodo al construir el heap; c2 = costo por paso del heap.
    Se estiman por mínimos cuadrados (sin intercepto) con todas las mediciones.
    """
    A = np.array([[r["N"], r["B"] * math.log2(r["N"])] for r in filas])
    t = np.array([r["tiempo_s"] for r in filas])
    (c1, c2), *_ = np.linalg.lstsq(A, t, rcond=None)
    pred = A @ np.array([c1, c2])
    r2 = 1 - ((t - pred) ** 2).sum() / ((t - t.mean()) ** 2).sum()
    return c1, c2, r2


def graficar(filas, eje, titulo, archivo, c1, c2):
    grafica_medido_vs_teoria(
        xs=[r[eje] for r in filas],
        medido_ms=[r["tiempo_s"] * 1e3 for r in filas],
        teoria_ms=[(c1 * r["N"] + c2 * r["B"] * math.log2(r["N"])) * 1e3 for r in filas],
        eje=eje, titulo=titulo, etiqueta_teoria=r"$c_1 N + c_2 B\log_2 N$ (ajuste)",
        ruta=os.path.join(SALIDA, archivo), log2_x=(eje == "N"))


def conteo_operaciones():
    """
    Cuenta comparaciones reales del heap y las compara con las cotas teóricas:
      heapify:  <= 2N comparaciones
      cada paso (heapreplace): <= 2*log2(N) comparaciones  -> total <= 2 B log2 N
    """
    filas = []
    for N in (2**k for k in range(6, 19, 2)):         # 64 ... 262 144
        B = 20 * N
        inst = instancia_reparto(N, B, semilla=N)
        c = ContadorComparaciones()
        voraz_heap(inst.utilidades, inst.B, contador=c)
        ch, cp = c.heapify, c.pasos
        filas.append({"N": N, "B": B, "cmp_heapify": ch, "cmp_pasos": cp,
                      "heapify/N": ch / N, "pasos/(B log2 N)": cp / (B * math.log2(N))})
        print(f"  N={N:>7}  B={B:>8}  heapify: {ch/N:.2f}·N   pasos: {cp/(B*math.log2(N)):.2f}·B·log2N")
    guardar_csv(os.path.join(SALIDA, "conteo.csv"), filas)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot([r["N"] for r in filas], [r["heapify/N"] for r in filas], "o-", label="comparaciones heapify / N")
    ax.plot([r["N"] for r in filas], [r["pasos/(B log2 N)"] for r in filas], "s-", label=r"comparaciones pasos / $(B\log_2 N)$")
    ax.axhline(2, color="gray", ls="--", lw=.8, label="cota teórica = 2")
    ax.set_xscale("log", base=2); ax.set_ylim(0, 2.5); ax.set_xlabel("N (B = 20N)")
    ax.set_title("Conteo de operaciones vs. cota teórica"); ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "conteo.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    print("Barrido 1: B fijo = 200 000, N creciente")
    f1 = barrido("variaN", [(N, 200_000) for N in (1_000, 4_000, 16_000, 64_000, 256_000, 1_024_000)])

    print("\nBarrido 2: N fijo = 10 000, B creciente")
    f2 = barrido("variaB", [(10_000, B) for B in (50_000, 100_000, 200_000, 400_000, 800_000, 1_600_000)])

    c1, c2, r2 = ajustar_constantes(f1 + f2)
    print(f"\nAjuste t = c1*N + c2*B*log2(N):  c1 = {c1:.2e} s/nodo,  c2 = {c2:.2e} s/paso,  R² = {r2:.4f}")
    graficar(f1, "N", "Variando N (B = 200 000)", "variaN.png", c1, c2)
    graficar(f2, "B", "Variando B (N = 10 000)", "variaB.png", c1, c2)

    print("\nConteo de comparaciones del montículo (independiente de la máquina)")
    conteo_operaciones()
    print(f"\nGráficas y CSV en {SALIDA}")
