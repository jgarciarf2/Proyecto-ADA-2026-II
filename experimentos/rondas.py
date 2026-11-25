"""Experimentos V2: costo al variar N y T, y calidad al variar la probabilidad p.

Ejecución desde la raíz: ``python -m experimentos.rondas``.
Los CSV y las figuras se guardan en resultados/variantes/v2/.
"""
import math
import os
import statistics

import matplotlib.pyplot as plt

from ada.casos_red import caso_red_sintetico, leer_caso_red
from ada.variantes.rondas import resolver_caso_red_v2
from experimentos.comun import carpeta_salida, guardar_csv, medir_mediana, grafica_medido_vs_teoria

SALIDA = carpeta_salida("variantes/v2")


def _caso(N, T, semilla):
    datos = caso_red_sintetico(f"v2_N{N}_T{T}_s{semilla}", N, T, min(6, N), 20, 30,
                               R=100, densidad=0.35, semilla=semilla)
    return leer_caso_red(datos)


def _unidad_teorica(N, T, k, B):
    return T * (N * N * k + B * math.log2(k + 1))


def _medir(nombre, pares):
    filas = []
    for N, T in pares:
        caso = _caso(N, T, 410 + N + T)
        k = min(caso.k, N)
        medir = lambda: resolver_caso_red_v2(caso, 0.2, semilla_fallas=19, con_optimo=False)
        t = medir_mediana(medir, reps=5)
        unidad = _unidad_teorica(N, T, k, caso.B)
        filas.append({"N": N, "T": T, "k": k, "B": caso.B, "tiempo_s": t,
                      "unidades_teoricas": unidad, "t_sobre_teoria": t / unidad})
        print(f"  N={N:>4} T={T:>3} k={k:>2} t={t*1e3:8.2f} ms t/teoría={t/unidad:.3e}")
    guardar_csv(os.path.join(SALIDA, f"{nombre}.csv"), filas)
    c = statistics.median(f["t_sobre_teoria"] for f in filas)
    eje = "N" if nombre == "variaN" else "T"
    grafica_medido_vs_teoria(
        xs=[f[eje] for f in filas], medido_ms=[f["tiempo_s"] * 1e3 for f in filas],
        teoria_ms=[c * f["unidades_teoricas"] * 1e3 for f in filas], eje=eje,
        titulo=("V2: variando N (T = 4)" if eje == "N" else "V2: variando T (N = 60)"),
        etiqueta_teoria=r"$c\,T(N^2k+B\log_2(k+1))$", ruta=os.path.join(SALIDA, f"{nombre}.png"))
    return filas


def calidad(probabilidades=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), repeticiones=30):
    """Estima la utilidad total esperada con semillas pareadas entre probabilidades."""
    caso = _caso(15, 5, 2026)
    filas, medias, errores = [], [], []
    for p in probabilidades:
        valores, fallas_prom = [], []
        for semilla in range(repeticiones):
            res = resolver_caso_red_v2(caso, p, semilla_fallas=semilla, con_optimo=False)
            valores.append(res["utilidad_conjunta_total"])
            fallas_prom.append(sum(len(r["caidos"]) for r in res["rondas"]) / (caso.T * caso.N))
        media = statistics.mean(valores)
        desv = statistics.pstdev(valores)
        filas.append({"probabilidad_falla": p, "repeticiones": repeticiones,
                      "utilidad_total_media": media, "desviacion_estandar": desv,
                      "fraccion_fallida_media": statistics.mean(fallas_prom)})
        medias.append(media); errores.append(desv)
        print(f"  p={p:.1f} utilidad media={media:.3f} desviación={desv:.3f} "
              f"fracción caída={statistics.mean(fallas_prom):.3f}")
    guardar_csv(os.path.join(SALIDA, "calidad_falla.csv"), filas)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.errorbar(probabilidades, medias, yerr=errores, marker="o", capsize=4, color="#2563eb")
    ax.set_xlabel("Probabilidad independiente de falla p")
    ax.set_ylabel("Utilidad conjunta total (media ± desviación)")
    ax.set_title(f"V2: utilidad al variar p (N=15, T=5, {repeticiones} semillas)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "calidad_falla.png"), dpi=150)
    plt.close(fig)
    return filas


if __name__ == "__main__":
    print("V2: tiempo al variar N, T=4")
    _medir("variaN", [(N, 4) for N in (20, 30, 40, 50, 60, 80)])
    print("\nV2: tiempo al variar T, N=60")
    _medir("variaT", [(60, T) for T in (1, 2, 4, 8, 12, 16)])
    print("\nV2: utilidad al variar probabilidad de falla")
    calidad()
    print(f"\nCSV y figuras en {SALIDA}")
