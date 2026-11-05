"""
Herramientas compartidas por todos los experimentos: carpeta de salida,
medición de tiempo, CSV y la gráfica "medido vs. teoría + cociente".
"""
import csv
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carpeta_salida(nombre):
    """resultados/<nombre>/, creada si no existe."""
    ruta = os.path.join(RAIZ, "resultados", nombre)
    os.makedirs(ruta, exist_ok=True)
    return ruta


def medir_mediana(funcion, reps=5):
    """Tiempo de funcion() en segundos: mediana de reps ejecuciones (resiste ruido del SO)."""
    tiempos = []
    for _ in range(reps):
        t0 = time.perf_counter()
        funcion()
        tiempos.append(time.perf_counter() - t0)
    return statistics.median(tiempos)


def guardar_csv(ruta, filas, columnas=None):
    """Si no hay filas (por ejemplo, una ronda sin participantes) escribe solo el encabezado."""
    columnas = list(filas[0].keys()) if filas else (columnas or [])
    with open(ruta, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)


def grafica_medido_vs_teoria(xs, medido_ms, teoria_ms, eje, titulo, etiqueta_teoria, ruta, log2_x=False):
    """
    Dos paneles: a la izquierda el tiempo medido y la curva teórica ajustada;
    a la derecha el cociente medido/predicho, que debe quedar cerca de 1.
    """
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.plot(xs, medido_ms, "o-", label="medido")
    a1.plot(xs, teoria_ms, "--", label=etiqueta_teoria)
    a1.set_xlabel(eje); a1.set_ylabel("tiempo (ms)"); a1.set_title(titulo)
    if log2_x:
        a1.set_xscale("log", base=2); a2.set_xscale("log", base=2)
    a1.legend(); a1.grid(alpha=.3)
    a2.plot(xs, [m / p for m, p in zip(medido_ms, teoria_ms)], "o-")
    a2.axhline(1, color="gray", lw=.8)
    a2.set_xlabel(eje); a2.set_ylabel("medido / predicho")
    a2.set_title("Cociente (≈ 1 si la teoría es correcta)")
    a2.set_ylim(0, 2); a2.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(ruta, dpi=130)
    plt.close(fig)
