"""
Figuras de la sección de variantes (docs/03_variantes.md).
Los valores se calculan con la utilidad de influencia de ada/, no se escriben a mano.

Uso:  python -m experimentos.figuras_variantes      -> docs/figuras/v1_*.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ada.parte2.fuerza_bruta import fuerza_bruta_general
from ada.parte2.influencia import f_influencia, matriz_influencia, voraz_influencia
from ada.variantes.costos import algoritmo_a
from experimentos.figuras_informe import AZUL, GRIS, NARANJA, TINTA, VERDE, guardar


def _valores(a, c, P, k):
    W = matriz_influencia(len(a), [])          # sin aristas: f(S) es la suma de los coeficientes
    simple = voraz_influencia(a, W, k, costos=c, presupuesto=P)[1]
    razon = voraz_influencia(a, W, k, costos=c, presupuesto=P, razon=True)[1]
    solo = max(f_influencia([i], a, W) for i in range(len(a)) if c[i] <= P)
    _, optimo = fuerza_bruta_general(lambda S: f_influencia(list(S), a, W), k, range(len(a)), c, P)
    return [simple, razon, solo, algoritmo_a(a, W, k, c, P)[1]], optimo


def contraejemplos_v1():
    """Los dos contraejemplos: cada voraz simple falla donde el otro acierta; el algoritmo A toma el mejor."""
    instancias = [
        ("Instancia 1: un nodo caro\nX (c = 10, f = 10) y Y₁…Y₅ (c = 2, f = 9)\nP = 10, k = 5",
         [10] + [9] * 5, [10] + [2] * 5, 10, 5),
        ("Instancia 2: un nodo barato\nA (c = 1, f = 2) y B (c = 10, f = 10)\nP = 10, k = 2",
         [2, 10], [1, 10], 10, 2),
    ]
    etiquetas = ["Voraz por\nganancia", "Voraz por\nrazón Δ/c", "Mejor nodo\nsolo", "Algoritmo A\n(máx. de los dos)"]
    colores = [GRIS, NARANJA, "#93c5fd", AZUL]
    fig, ejes = plt.subplots(1, 2, figsize=(10.5, 4.3))
    for ax, (titulo, a, c, P, k) in zip(ejes, instancias):
        valores, optimo = _valores(a, c, P, k)
        barras = ax.bar(range(4), valores, color=colores, width=0.62, edgecolor="white")
        ax.axhline(optimo, color=VERDE, lw=1.6, ls="--", label=f"óptimo (fuerza bruta) = {optimo:g}")
        ax.legend(loc="upper left", fontsize=8.5, frameon=False)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v + optimo * 0.015, f"{v:g}", ha="center", va="bottom",
                    fontsize=9.5, color=TINTA, fontweight="bold")
        ax.set_xticks(range(4), etiquetas, fontsize=8.5)
        ax.set_ylim(0, optimo * 1.32)
        ax.set_ylabel("utilidad conjunta f(S)")
        ax.set_title(titulo, fontsize=9.5, loc="left")
    fig.tight_layout(w_pad=3)
    guardar(fig, "v1_contraejemplos.png")


if __name__ == "__main__":
    contraejemplos_v1()
