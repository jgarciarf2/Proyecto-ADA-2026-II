"""
Experimentos de la Parte 2 con la utilidad de influencia (la de los casos de la profesora).

1) Tiempo del voraz al variar N (k fijo) y k (N fijo), comparado contra T(N, k) = c·N²·k.
   Además se cuentan las evaluaciones de ganancia, que deben ser exactamente kN − k(k−1)/2.
2) Cota (1 − 1/e) en datos propios: 300 instancias pequeñas, voraz contra el óptimo por
   fuerza bruta, sin costos (la cota está garantizada) y con costos (no lo está).

Uso:  python -m experimentos.influencia
"""
import math
import os
import random
import statistics

import matplotlib.pyplot as plt
import numpy as np

from ada.generadores import instancia_influencia
from ada.parte2.fuerza_bruta import fuerza_bruta_general
from ada.parte2.influencia import f_influencia, voraz_influencia
from experimentos.comun import carpeta_salida, grafica_medido_vs_teoria, guardar_csv, medir_mediana

SALIDA = carpeta_salida("influencia")
COTA = 1 - 1 / math.e


def barrido(nombre, pares):
    filas = []
    for N, k in pares:
        inst = instancia_influencia(N, semilla=N * 31 + k)
        t = medir_mediana(lambda: voraz_influencia(inst.a, inst.W, k), reps=7)
        _, _, ev = voraz_influencia(inst.a, inst.W, k, contar=True)
        esperado = k * N - k * (k - 1) // 2
        filas.append({"N": N, "k": k, "tiempo_s": t, "evaluaciones": ev, "eval_teoricas": esperado,
                      "t/(N^2 k)": t / (N * N * k)})
        print(f"  N={N:>5} k={k:>3}  t={t*1e3:9.1f} ms  evaluaciones={ev:>7} (teoría {esperado:>7})  "
              f"t/(N²k)={t/(N*N*k):.2e}")
    guardar_csv(os.path.join(SALIDA, f"{nombre}.csv"), filas)
    return filas


def graficar(filas, eje, titulo, archivo):
    c = statistics.median(r["t/(N^2 k)"] for r in filas)
    grafica_medido_vs_teoria(
        xs=[r[eje] for r in filas], medido_ms=[r["tiempo_s"] * 1e3 for r in filas],
        teoria_ms=[c * r["N"] ** 2 * r["k"] * 1e3 for r in filas], eje=eje, titulo=titulo,
        etiqueta_teoria=r"$c\cdot N^2 k$", ruta=os.path.join(SALIDA, archivo))


def verificar_cota(casos=300):
    filas = []
    for s in range(casos):
        rng = random.Random(s)
        N, k = rng.randint(8, 12), rng.randint(2, 4)
        inst = instancia_influencia(N, semilla=s, densidad=rng.uniform(0.3, 0.9))
        valor = lambda A: f_influencia(A, inst.a, inst.W)
        _, v = voraz_influencia(inst.a, inst.W, k)
        _, opt = fuerza_bruta_general(valor, k, range(N))
        P = rng.randint(5, 12)
        _, vc = voraz_influencia(inst.a, inst.W, k, costos=inst.costos, presupuesto=P)
        _, optc = fuerza_bruta_general(valor, k, range(N), costos=inst.costos, presupuesto=P)
        filas.append({"semilla": s, "N": N, "k": k, "P": P, "voraz": v, "optimo": opt, "razon": v / opt,
                      "voraz_costos": vc, "optimo_costos": optc, "razon_costos": vc / optc if optc else 1.0})
    guardar_csv(os.path.join(SALIDA, "cota.csv"), filas)
    sin = [r["razon"] for r in filas]
    con = [r["razon_costos"] for r in filas]
    print(f"Cota sin costos: mínimo {min(sin):.4f} (cota {COTA:.4f}), óptimo exacto en "
          f"{sum(x > 1 - 1e-9 for x in sin)}/{casos} | {'TODAS cumplen' if min(sin) >= COTA else 'HAY VIOLACIONES'}")
    print(f"Con costos (sin garantía): mínimo {min(con):.4f}, óptimo exacto en "
          f"{sum(x > 1 - 1e-9 for x in con)}/{casos}, por debajo de 1 − 1/e: {sum(x < COTA for x in con)}")

    # escala logarítmica en y: así se ven también las barras de 1 sola instancia
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    bordes = np.linspace(0.35, 1.0, 53)
    for ax, datos, titulo in [(a1, sin, "Solo cupo k (cota garantizada)"), (a2, con, "Cupo k y costos ≤ P (sin garantía)")]:
        _, _, barras = ax.hist(datos, bins=bordes, color="#2563eb", edgecolor="white")
        for b in barras:
            if b.get_x() + b.get_width() <= COTA:
                b.set_color("#dc2626")
        ax.axvline(COTA, color="#dc2626", ls="--", label=f"1 − 1/e ≈ {COTA:.3f}")
        debajo = sum(x < COTA for x in datos)
        ax.set_title(f"{titulo}\nmínimo {min(datos):.3f} · por debajo de la cota: {debajo}", fontsize=10)
        ax.set_xlabel("utilidad del voraz / utilidad óptima"); ax.legend(frameon=False, fontsize=8.5, loc="upper left")
        ax.set_yscale("log"); ax.grid(alpha=.3)
    a1.set_ylabel("instancias (escala log)")
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "cota.png"), dpi=150); plt.close(fig)


if __name__ == "__main__":
    print("Voraz de influencia, k fijo = 10, N creciente (grafo completo)")
    f1 = barrido("variaN", [(N, 10) for N in (50, 100, 200, 300, 400, 600, 800)])
    graficar(f1, "N", "Voraz de influencia: variando N (k = 10)", "variaN.png")
    print("\nVoraz de influencia, N fijo = 400, k creciente")
    f2 = barrido("variak", [(400, k) for k in (5, 10, 20, 40, 80)])
    graficar(f2, "k", "Voraz de influencia: variando k (N = 400)", "variak.png")
    print()
    verificar_cota()
    print(f"\nGráficas y CSV en {SALIDA}")
