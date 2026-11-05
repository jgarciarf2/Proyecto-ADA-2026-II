"""
Diagramas UML del manual técnico: componentes, clases y secuencia.
Los nombres de clases, atributos y funciones son los del código de ada/.

Uso:  python -m experimentos.figuras_manual      -> docs/figuras/manual_*.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from experimentos.comun import RAIZ

SALIDA = os.path.join(RAIZ, "docs", "figuras")
AZUL, NARANJA, VERDE, ROJO, GRIS, TINTA = "#2563eb", "#ea7a2b", "#16a34a", "#dc2626", "#64748b", "#1e293b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})


def guardar(fig, nombre):
    os.makedirs(SALIDA, exist_ok=True)
    fig.savefig(os.path.join(SALIDA, nombre), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", nombre)


def flecha(ax, a, b, estilo="-|>", color="#475569", ls="-", texto=None, desplaz=(0, 0.08), tam=7.5, **kw):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=12, lw=1.2, color=color,
                                 linestyle=ls, **kw))
    if texto:
        ax.text((a[0] + b[0]) / 2 + desplaz[0], (a[1] + b[1]) / 2 + desplaz[1], texto, fontsize=tam,
                color=color, ha="center", va="bottom")


# ---------------------------------------------------------------------------
def componentes():
    """Diagrama de componentes: carpetas del proyecto y sus dependencias."""
    fig, ax = plt.subplots(figsize=(11, 6.8)); ax.axis("off"); ax.set_xlim(0, 22); ax.set_ylim(0, 13.4)

    def comp(x, y, w, h, titulo, filas, color, borde):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=color, ec=borde, lw=1.4))
        ax.add_patch(Rectangle((x + w - 0.7, y + h - 0.55), 0.45, 0.32, fc="white", ec=borde, lw=0.9))
        ax.text(x + 0.25, y + h - 0.4, titulo, fontweight="bold", fontsize=9.3, va="center", color=TINTA)
        for j, f in enumerate(filas):
            ax.text(x + 0.3, y + h - 1.0 - 0.46 * j, f, fontsize=7.8, va="center", color="#334155", family="DejaVu Sans Mono")

    comp(0.3, 9.6, 5.6, 3.3, "«datos» casos/", ["profesora/*.json", "propios/*.json", "ejemplos/*.json"], "#f8fafc", GRIS)
    comp(7.4, 9.6, 6.9, 3.3, "«interfaz» app/ (Streamlit)", ["principal.py · paginas.py", "vista_resultado.py · vista_red.py",
                                                           "graficas.py · estilos.py"], "#f5f3ff", "#7c3aed")
    comp(15.8, 9.6, 5.9, 3.3, "«pruebas» tests/", ["test_parte1.py · test_parte2.py", "test_ronda.py · test_casos.py",
                                                  "test_red.py"], "#f0fdf4", VERDE)
    comp(0.3, 4.6, 5.6, 3.7, "«CLI» experimentos/", ["casos.py       evidencia", "parte1.py · parte2.py", "influencia.py  tiempos",
                                                     "comun.py", "figuras_*.py"], "#fff7ed", NARANJA)
    # núcleo: el título va arriba y los módulos debajo, sin tocarse
    ax.add_patch(FancyBboxPatch((7.4, 2.9), 14.3, 5.7, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#eff6ff", ec=AZUL, lw=1.4))
    ax.text(7.65, 8.2, "«núcleo» ada/   solo calcula: no imprime ni escribe archivos", fontweight="bold", fontsize=9.3,
            va="center", color=TINTA)
    modulos = [(7.75, 5.75, "casos_red.py", "lee y valida el\nformato de la profesora"),
               (11.25, 5.75, "solucion_red.py", "T rondas: seleccionar,\nrepartir y verificar"),
               (14.75, 5.75, "verificacion.py", "restricciones y\nvalores recalculados"),
               (18.25, 5.75, "utilidades.py", "a·ln(1+x), tope, tabla,\nraíz, saturación"),
               (7.75, 3.2, "parte2/", "voraz_general, influencia\nfuerza_bruta, reduccion"),
               (11.25, 3.2, "parte1/", "voraz_heap\nexacto_dp"),
               (14.75, 3.2, "casos.py", "formato provisional\ny ronda.py (sintéticos)"),
               (18.25, 3.2, "modelo.py", "dataclasses y\ngeneradores.py")]
    for x, y, t, d in modulos:
        ax.add_patch(FancyBboxPatch((x, y), 3.15, 2.0, boxstyle="round,pad=0.02,rounding_size=0.1", fc="white", ec=AZUL, lw=1))
        ax.text(x + 1.575, y + 1.6, t, ha="center", fontweight="bold", fontsize=7.9, color=TINTA)
        ax.text(x + 1.575, y + 0.75, d, ha="center", va="center", fontsize=7.2, color="#475569", linespacing=1.3)
    comp(0.3, 0.2, 5.6, 3.0, "«salida» resultados/", ["casos/<nombre>/", "  resultado.json y CSV", "parte1/ parte2/ influencia/"],
         "#f8fafc", GRIS)

    flecha(ax, (3.1, 9.6), (3.1, 8.3), texto="lee JSON", desplaz=(0.85, -0.15))
    flecha(ax, (5.9, 6.4), (7.4, 6.4), texto="usa")
    flecha(ax, (3.1, 4.6), (3.1, 3.2), texto="escribe", desplaz=(0.85, -0.15))
    flecha(ax, (10.85, 9.6), (10.85, 8.6), texto="usa", desplaz=(0.4, -0.12))
    flecha(ax, (7.4, 10.2), (5.9, 7.6), texto="ejecutar_caso\nguardar_evidencia", desplaz=(1.05, -0.25), tam=7.2)
    flecha(ax, (18.75, 9.6), (18.75, 8.6), texto="prueba", desplaz=(0.55, -0.12))
    guardar(fig, "manual_componentes.png")


# ---------------------------------------------------------------------------
def clase(ax, x, y, w, nombre, atributos, metodos, color="#eff6ff", borde=AZUL, estereotipo=None):
    """Caja UML de clase con tres compartimentos. Devuelve (x, y_abajo, w, alto)."""
    lh = 0.36
    h_nom = 0.62 + (0.3 if estereotipo else 0)
    h_at = max(1, len(atributos)) * lh + 0.15
    h_me = max(1, len(metodos)) * lh + 0.15
    alto = h_nom + h_at + h_me
    ya = y - alto
    ax.add_patch(Rectangle((x, ya), w, alto, fc="white", ec=borde, lw=1.2))
    ax.add_patch(Rectangle((x, y - h_nom), w, h_nom, fc=color, ec=borde, lw=1.2))
    if estereotipo:
        ax.text(x + w / 2, y - 0.25, f"«{estereotipo}»", ha="center", va="center", fontsize=7, color="#475569")
    ax.text(x + w / 2, y - h_nom + 0.3, nombre, ha="center", va="center", fontweight="bold", fontsize=8.6, color=TINTA)
    ax.plot([x, x + w], [y - h_nom - h_at] * 2, color=borde, lw=1)
    for j, a in enumerate(atributos):
        ax.text(x + 0.12, y - h_nom - 0.3 - lh * j, a, fontsize=7.1, va="center", family="DejaVu Sans Mono")
    for j, m in enumerate(metodos):
        ax.text(x + 0.12, y - h_nom - h_at - 0.3 - lh * j, m, fontsize=7.1, va="center", family="DejaVu Sans Mono")
    return x, ya, w, alto


def clases():
    fig, ax = plt.subplots(figsize=(13, 9.6)); ax.axis("off"); ax.set_xlim(0, 26.4); ax.set_ylim(0.6, 19.2)
    ax.text(0.2, 18.9, "paquete ada.utilidades", fontsize=9, color=GRIS, fontweight="bold")
    base = clase(ax, 10.2, 18.6, 5.6, "Utilidad", [], ["__call__(x) -> float", "marginal(x) = u(x+1) − u(x)"],
                 color="#fff7ed", borde=NARANJA, estereotipo="abstracta")
    hijas = [(0.2, "UtilidadLog", ["a: float"], ["__call__ = a·ln(1+x)"]),
             (5.45, "UtilidadRaiz", ["a: float"], ["__call__ = a·√x"]),
             (10.7, "UtilidadSaturacion", ["a: float", "b: float"], ["__call__ = a(1−e^(−bx))"]),
             (15.95, "UtilidadTabla", ["valores: list[float]"], ["__call__ = valores[x]"]),
             (21.2, "UtilidadConTope", ["base: Utilidad", "tope: int"], ["__call__ = base(min(x, tope))"])]
    y_hijas, y_bus = 15.2, 15.75
    for x, n, at, me in hijas:
        clase(ax, x, y_hijas, 5.0, n, at, me, color="#fff7ed", borde=NARANJA)
        ax.plot([x + 2.5, x + 2.5], [y_hijas, y_bus], color=NARANJA, lw=1.2)
    # herencia en forma de árbol: una barra común y un solo triángulo hueco hacia la clase base
    ax.plot([2.7, 23.7], [y_bus, y_bus], color=NARANJA, lw=1.2)
    ax.plot([13.0, 13.0], [y_bus, base[1] - 0.3], color=NARANJA, lw=1.2)
    ax.add_patch(Polygon([[13.0, base[1]], [12.75, base[1] - 0.32], [13.25, base[1] - 0.32]], closed=True,
                         fc="white", ec=NARANJA, lw=1.2))
    # composición: UtilidadConTope contiene otra Utilidad (rombo relleno del lado del contenedor)
    ax.plot([26.0, 26.0, 15.8], [y_hijas - 0.5, 17.6, 17.6], color=NARANJA, lw=1.2, ls="--")
    ax.add_patch(Polygon([[26.0, y_hijas - 0.5], [25.85, y_hijas - 0.2], [26.0, y_hijas + 0.1], [26.15, y_hijas - 0.2]],
                         closed=True, fc=NARANJA, ec=NARANJA))
    ax.text(20.9, 17.75, "base: Utilidad  (composición)", fontsize=7.4, color=NARANJA, ha="center")

    ax.text(0.2, 11.6, "paquetes ada.casos_red y ada.casos", fontsize=9, color=GRIS, fontweight="bold")
    red = clase(ax, 0.2, 11.3, 6.3, "CasoRed", ["nombre: str", "ids: list", "a: list[float]", "W: list[list[float]]",
                                               "costos: list", "presupuesto_nodo: list[int]", "T, k, B, P: int"],
                ["N -> int  «propiedad»"], estereotipo="dataclass")
    caso = clase(ax, 7.1, 11.3, 6.1, "Caso", ["nombre: str", "ids: list", "conjuntos: list[frozenset]",
                                             "pesos: list[float]", "utilidades: list[Utilidad]", "k, B: int"],
                 ["N, M -> int  «propiedad»"], estereotipo="dataclass")
    inv = clase(ax, 3.6, 4.1, 6.3, "CasoInvalido", [], ["mensaje: qué campo falla y dónde"],
                color="#fef2f2", borde=ROJO, estereotipo="excepción · hereda de ValueError")
    flecha(ax, (3.35, red[1]), (5.0, 4.1), ls="--", color=ROJO, texto="leer_caso_red() lanza", desplaz=(-1.75, 0))
    flecha(ax, (10.15, caso[1]), (8.6, 4.1), ls="--", color=ROJO, texto="leer_caso() lanza", desplaz=(1.3, 0))

    ax.text(14.0, 11.6, "paquete ada.modelo", fontsize=9, color=GRIS, fontweight="bold")
    clase(ax, 14.0, 11.3, 5.6, "InstanciaReparto", ["utilidades: list[Utilidad]", "B: int"], ["N"], estereotipo="dataclass")
    clase(ax, 14.0, 8.2, 5.6, "InstanciaCobertura", ["conjuntos: list", "pesos: list"], ["N, M"], estereotipo="dataclass")
    clase(ax, 14.0, 5.1, 5.6, "InstanciaInfluencia", ["a: list", "W: list[list]", "costos: list"], ["N"], estereotipo="dataclass")
    ax.text(20.4, 11.6, "estado de los algoritmos", fontsize=9, color=GRIS, fontweight="bold")
    est = clase(ax, 20.4, 11.3, 5.6, "EstadoInfluencia", ["a: list", "W: list[list]", "q: list[float]"],
                ["ganancia(i) -> float  O(N)", "agregar(j)            O(N)"], color="#f0fdf4", borde=VERDE)
    ax.text(20.45, est[1] - 0.4, "lo crea voraz_influencia(a, W, …)\ncon los datos de CasoRed", fontsize=7.2,
            color="#475569", va="top")
    clase(ax, 20.4, 6.6, 5.6, "ContadorComparaciones", ["total: int", "heapify: int", "par: type"],
          ["fin_heapify()", "pasos -> int  «propiedad»"], color="#f0fdf4", borde=VERDE)
    ax.text(20.45, 2.75, "lo usa voraz_heap(…, contador=…)\npara contar comparaciones", fontsize=7.2, color="#475569", va="top")
    ax.text(0.2, 0.9, "Triángulo hueco = herencia · rombo relleno = composición · punteada = dependencia. "
            "Los algoritmos (voraz_heap, voraz_general, resolver_caso_red, …) son funciones, no clases.",
            fontsize=7.5, color="#475569")
    guardar(fig, "manual_clases.png")


# ---------------------------------------------------------------------------
def secuencia():
    """Diagrama de secuencia de: python -m experimentos.casos casos/profesora/"""
    fig, ax = plt.subplots(figsize=(13.5, 9)); ax.axis("off"); ax.set_xlim(0, 27); ax.set_ylim(0, 18)
    vidas = [("cli", "experimentos\n.casos", 1.7), ("lector", "ada\n.casos_red", 5.6), ("sol", "ada\n.solucion_red", 9.6),
             ("sel", "ada.parte2\nvoraz_influencia", 13.7), ("rep", "ada.parte1\nvoraz_heap", 17.4),
             ("ver", "ada\n.verificacion", 20.9), ("fb", "ada.parte2\nfuerza_bruta", 24.6)]
    x = {clave: px for clave, _, px in vidas}
    for _, n, px in vidas:
        ax.add_patch(FancyBboxPatch((px - 1.5, 16.5), 3.0, 1.15, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#eff6ff", ec=AZUL))
        ax.text(px, 17.07, n, ha="center", va="center", fontsize=7.6, fontweight="bold", linespacing=1.15)
        ax.plot([px, px], [0.5, 16.5], color="#94a3b8", ls="--", lw=1)

    def msg(de, a, y, texto, ret=False):
        derecha = x[a] > x[de]
        flecha(ax, (x[de] + (0.15 if derecha else -0.15), y), (x[a] + (-0.15 if derecha else 0.15), y),
               estilo="->" if ret else "-|>", ls="--" if ret else "-", color=GRIS if ret else TINTA)
        # la etiqueta empieza justo después de la barra de activación, para no quedar encima de ella
        ax.text(min(x[de], x[a]) + 0.35, y + 0.07, texto, fontsize=7.3, color=GRIS if ret else TINTA,
                ha="left", va="bottom")

    def activo(n, y1, y2):
        ax.add_patch(Rectangle((x[n] - 0.13, y2), 0.26, y1 - y2, fc="white", ec=TINTA, lw=1, zorder=3))

    activo("cli", 16.2, 0.8)
    ax.text(x["cli"] + 0.3, 15.75, "json.load(archivo)", fontsize=7.4)
    msg("cli", "lector", 15.0, "es_formato_red(datos)")
    msg("lector", "cli", 14.45, "True", ret=True)
    msg("cli", "lector", 13.8, "leer_caso_red(datos)")
    activo("lector", 13.8, 13.0)
    msg("lector", "cli", 13.0, "CasoRed  (o CasoInvalido)", ret=True)
    msg("cli", "sol", 12.2, "resolver_caso_red(caso)")
    activo("sol", 12.2, 2.4)

    ax.add_patch(Rectangle((7.0, 2.85), 19.6, 8.85, fc="none", ec=TINTA, lw=1))
    ax.add_patch(Rectangle((7.0, 11.2), 2.3, 0.5, fc="#f1f5f9", ec=TINTA, lw=1))
    ax.text(7.12, 11.45, "loop [t = 1..T]", fontsize=7.8, va="center", fontweight="bold")
    msg("sol", "sel", 10.6, "voraz_influencia(a, W, k, candidatos, costos, P)")
    activo("sel", 10.6, 9.75)
    msg("sel", "sol", 9.75, "Sₜ, f(Sₜ), traza de selección", ret=True)
    msg("sol", "rep", 9.0, "voraz_heap(utilidades con tope, B)")
    activo("rep", 9.0, 8.2)
    msg("rep", "sol", 8.2, "xₜ, U(xₜ), traza de reparto", ret=True)
    msg("sol", "ver", 7.45, "verificar_seleccion, _reparto, _valor")
    activo("ver", 7.45, 6.7)
    msg("ver", "sol", 6.7, "registros {restriccion, cumple, detalle}", ret=True)
    ax.add_patch(Rectangle((7.3, 3.7), 19.0, 2.55, fc="none", ec=GRIS, lw=1, ls="--"))
    ax.add_patch(Rectangle((7.3, 5.6), 2.05, 0.65, fc="#f8fafc", ec=GRIS, lw=1))
    ax.text(7.4, 5.92, "opt [≤ 200 000\n grupos]", fontsize=7, va="center")
    msg("sol", "fb", 5.2, "fuerza_bruta_general(f, k, candidatos, costos, P)")
    activo("fb", 5.2, 4.3)
    msg("fb", "sol", 4.3, "óptimo de referencia", ret=True)
    ax.text(x["sol"] + 0.3, 3.15, "actualizar saldos: rᵢ ← rᵢ − xᵢ", fontsize=7.4)
    msg("sol", "cli", 2.4, "dict: rondas, totales, verificaciones, tiempos", ret=True)
    ax.text(x["cli"] + 0.3, 1.75, "guardar_evidencia(): resultado.json y CSV", fontsize=7.4)
    ax.text(x["cli"] + 0.3, 1.2, "actualizar_resumen(): resumen.csv", fontsize=7.4)
    guardar(fig, "manual_secuencia.png")


if __name__ == "__main__":
    print(f"Figuras del manual en {SALIDA}")
    componentes(); clases(); secuencia()
