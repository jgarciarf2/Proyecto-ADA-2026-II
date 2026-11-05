"""
Figuras del documento de formulación (docs/formulacion.md e informe en Word).
Todo se calcula con el mismo código de ada/, así que las figuras coinciden con la implementación.

Uso:  python -m experimentos.figuras_informe      -> docs/figuras/*.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon

from ada.casos_red import leer_caso_red
from ada.parte2.influencia import f_influencia, matriz_influencia
from ada.utilidades import UtilidadConTope, UtilidadLog
from experimentos.comun import RAIZ

SALIDA = os.path.join(RAIZ, "docs", "figuras")
AZUL, NARANJA, VERDE, ROJO, GRIS, TINTA = "#2563eb", "#ea7a2b", "#16a34a", "#dc2626", "#cbd2dc", "#1e293b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold"})


def guardar(fig, nombre):
    os.makedirs(SALIDA, exist_ok=True)
    fig.savefig(os.path.join(SALIDA, nombre), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", nombre)


def caja(ax, x, y, w, h, texto, color="#eff4ff", borde=AZUL, tam=9.5):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=color, ec=borde, lw=1.4))
    ax.text(x, y, texto, ha="center", va="center", fontsize=tam, color=TINTA, linespacing=1.35)


def flecha(ax, x1, y1, x2, y2, texto=None, estilo="-|>", **kw):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=estilo, mutation_scale=13, lw=1.3,
                                 color="#475569", **kw))
    if texto:
        ax.text((x1 + x2) / 2 + 0.12, (y1 + y2) / 2, texto, fontsize=8.5, color="#475569", va="center")


# ---------------------------------------------------------------------------
def flujo_ronda():
    """Diagrama de actividades (UML) de la solución base para un caso de T rondas."""
    fig, ax = plt.subplots(figsize=(7.2, 9.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 13.2); ax.axis("off")
    ax.add_patch(Circle((5, 12.75), 0.22, color=TINTA))
    pasos = [
        (11.55, "Leer y validar el caso\nt ← 1,  rᵢ ← Rᵢ para todo nodo i"),
        (10.05, "Candidatos de la ronda\nV⁽ᵗ⁾ = { i : rᵢ > 0 }"),
        (8.45, "Parte 2 · Selección (voraz de influencia)\nSₜ con |Sₜ| ≤ k  y  Σ cᵢ ≤ P\nmaximizando f(Sₜ)"),
        (6.75, "Parte 1 · Reparto (voraz con montículo)\nxᵢ con Σ xᵢ ≤ B  y  0 ≤ xᵢ ≤ rᵢ\nmaximizando Σ uᵢ(xᵢ)"),
        (5.15, "Verificar restricciones\ny recalcular f(Sₜ) y U(xₜ)"),
        (3.75, "Actualizar saldos\nrᵢ ← rᵢ − xᵢ para i ∈ Sₜ ;  t ← t + 1"),
    ]
    alto = {11.55: 0.95, 10.05: 0.95, 8.45: 1.2, 6.75: 1.2, 5.15: 0.95, 3.75: 0.95}
    flecha(ax, 5, 12.53, 5, 11.55 + 0.48)
    for (y, t), (y2, _) in zip(pasos, pasos[1:] + [(2.4, "")]):
        color = "#fff4eb" if "Parte 1" in t else ("#eff4ff" if "Parte 2" in t else "#f8fafc")
        borde = NARANJA if "Parte 1" in t else (AZUL if "Parte 2" in t else "#64748b")
        caja(ax, 5, y, 6.6, alto[y], t, color, borde)
        destino = y2 + (alto.get(y2, 0.9) / 2 if y2 != 2.4 else 0.55)
        flecha(ax, 5, y - alto[y] / 2, 5, destino)
    ax.add_patch(Polygon([[5, 2.95], [5.85, 2.4], [5, 1.85], [4.15, 2.4]], closed=True, fc="white", ec=TINTA, lw=1.3))
    ax.text(5, 2.4, "t ≤ T ?", ha="center", va="center", fontsize=9.5)
    ax.plot([5.85, 8.9, 8.9, 8.3], [2.4, 2.4, 10.05, 10.05], color="#475569", lw=1.3)
    flecha(ax, 8.9, 10.05, 8.32, 10.05)
    ax.text(7.2, 2.62, "sí", fontsize=9, color="#475569")
    flecha(ax, 5, 1.85, 5, 1.05, "no")
    ax.add_patch(Circle((5, 0.8), 0.25, fc="white", ec=TINTA, lw=1.5))
    ax.add_patch(Circle((5, 0.8), 0.15, color=TINTA))
    ax.text(5.45, 0.8, "Resultado, tiempos y trazas de las T rondas", va="center", fontsize=9)
    guardar(fig, "fig01_flujo_ronda.png")


# ---------------------------------------------------------------------------
EJ_A = [5, 3, 3, 5, 1]
EJ_N = "ABCDE"
EJ_E = [(0, 3, 0.2), (1, 2, 0.6), (1, 4, 0.2), (2, 3, 0.2), (3, 4, 0.4)]
EJ_POS = {0: (0.2, 1.8), 1: (2.4, 2.6), 2: (1.8, 1.2), 3: (0.9, 0.1), 4: (3.6, 0.8)}
# dónde va el texto "a · p" de cada nodo, para que no tape aristas
EJ_ETIQ = {0: (0.2, 2.28, "center"), 1: (2.78, 2.6, "left"), 2: (2.18, 1.2, "left"), 3: (0.9, -0.42, "center"),
           4: (3.6, 0.32, "center")}


def grafo_ejemplo():
    W = matriz_influencia(5, EJ_E)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.3))
    for ax, S, titulo in [(axs[0], [3, 1], "Voraz: S = {D, B},  f(S) = 11,56"),
                          (axs[1], [0, 2], "Óptimo: S = {A, C},  f(S) = 11,60")]:
        ax.set_xlim(-0.6, 4.6); ax.set_ylim(-0.7, 3.0); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(titulo, fontsize=10.5)
        for u, v, w in EJ_E:
            (x1, y1), (x2, y2) = EJ_POS[u], EJ_POS[v]
            ax.plot([x1, x2], [y1, y2], color="#94a3b8", lw=1 + 4 * w, zorder=1)
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{w:g}", fontsize=8.5, ha="center", va="center",
                    bbox=dict(fc="white", ec="none", pad=0.6), zorder=2)
        for v in range(5):
            q = 1.0
            for u in S:
                q *= 1 - W[u][v]
            p = 1 - q
            x, y = EJ_POS[v]
            ax.add_patch(Circle((x, y), 0.28, fc=(0.15, 0.39, 0.92, 0.12 + 0.75 * p),
                                ec=TINTA if v in S else "#64748b", lw=2.6 if v in S else 1.2, zorder=3))
            ax.text(x, y, EJ_N[v], ha="center", va="center", fontsize=11, fontweight="bold",
                    color="white" if p > 0.6 else TINTA, zorder=4)
            ex, ey, al = EJ_ETIQ[v]
            ax.text(ex, ey, f"a={EJ_A[v]} · p={p:.2f}", ha=al, va="center", fontsize=8, color="#334155", zorder=4)
    fig.text(0.5, -0.02, "Borde grueso = nodo elegido. Color = probabilidad p de quedar influido por S. "
             "Grosor de la arista = peso de influencia.", ha="center", fontsize=8.5, color="#475569")
    guardar(fig, "fig02_grafo_ejemplo.png")


# ---------------------------------------------------------------------------
P1_A, P1_R, P1_B = [6, 3, 2], [3, 6, 6], 6
P1_X = [3, 2, 1]


def utilidad_concava():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.8))
    xs = range(0, 7)
    for a, r, c in zip(P1_A, P1_R, [AZUL, NARANJA, VERDE]):
        u = UtilidadConTope(UtilidadLog(a), r)
        a1.plot(list(xs), [u(x) for x in xs], "o-", color=c, label=f"a = {a}, tope r = {r}")
    a1.set_xlabel("unidades de ruido x"); a1.set_ylabel("utilidad ûᵢ(x)")
    a1.set_title("Utilidad con tope: creciente y cóncava"); a1.legend(fontsize=8.5, frameon=False)
    a1.annotate("después del tope\nla curva es plana", xy=(4.5, 6 * 1.3863), xytext=(3.2, 6.6), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color="#475569"))
    ancho = 0.26
    for j, (a, r, c) in enumerate(zip(P1_A, P1_R, [AZUL, NARANJA, VERDE])):
        u = UtilidadConTope(UtilidadLog(a), r)
        a2.bar([t + (j - 1) * ancho for t in range(1, 7)], [u.marginal(t - 1) for t in range(1, 7)], ancho,
               color=c, label=f"nodo {j + 1}")
    a2.set_xlabel("número de la unidad t"); a2.set_ylabel("ganancia marginal gᵢ(t)")
    a2.set_title("Ganancias marginales: no crecen"); a2.legend(fontsize=8.5, frameon=False)
    guardar(fig, "fig03_utilidad_concava.png")


def nivel_agua():
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    x0 = 0
    for j, (a, r) in enumerate(zip(P1_A, P1_R)):
        u = UtilidadConTope(UtilidadLog(a), r)
        for t in range(1, 6):
            g = u.marginal(t - 1)
            if g <= 0:
                ax.bar(x0 + t, 0.05, 0.75, color="white", edgecolor=GRIS, hatch="///")
                continue
            ax.bar(x0 + t, g, 0.75, color=AZUL if t <= P1_X[j] else GRIS)
            ax.text(x0 + t, g + 0.07, f"{g:.2f}", ha="center", fontsize=7.5, color="#334155")
        ax.text(x0 + 3, -0.55, f"nodo {j + 1}  (a={a}, r={r})\nxᵢ = {P1_X[j]}", ha="center", fontsize=9)
        x0 += 6.5
    ax.axhspan(0.863, 1.216, color=NARANJA, alpha=0.12)
    ax.axhline(1.0, color=NARANJA, ls="--", lw=1.6)
    ax.annotate("nivel λ ∈ (0,863 ; 1,216]", xy=(12.6, 1.0), xytext=(12.6, 3.0), color=NARANJA, fontsize=9,
                ha="center", arrowprops=dict(arrowstyle="->", color=NARANJA))
    ax.set_xticks([]); ax.set_ylim(-0.95, 4.6); ax.set_ylabel("ganancia marginal")
    ax.spines["bottom"].set_visible(False)
    ax.set_title("Reparto óptimo con B = 6: las 6 unidades entregadas (azul) valen más que cualquier otra")
    guardar(fig, "fig04_nivel_agua.png")


# ---------------------------------------------------------------------------
def reduccion_cobertura():
    fig, ax = plt.subplots(figsize=(9.5, 3.9)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(-0.4, 4.2)
    conjuntos = {"S₁": [1, 2, 3], "S₂": [4, 5, 6], "S₃": [1, 2, 4, 5]}
    ys = {"S₁": 3.2, "S₂": 1.9, "S₃": 0.6}
    ye = {e: 3.6 - 0.6 * (e - 1) for e in range(1, 7)}
    ax.text(1.0, 4.05, "Cobertura Máxima", ha="center", fontweight="bold")
    ax.text(5.7, 4.05, "Caso de selección construido", ha="center", fontweight="bold")
    for s, y in ys.items():
        caja(ax, 0.6, y, 0.8, 0.5, s, "#f8fafc", "#64748b")
        for e in conjuntos[s]:
            ax.plot([1.0, 2.3], [y, ye[e]], color="#94a3b8", lw=1)
    for e, y in ye.items():
        ax.add_patch(Circle((2.5, y), 0.18, fc="white", ec="#64748b")); ax.text(2.5, y, str(e), ha="center", va="center", fontsize=8.5)
    flecha(ax, 3.1, 1.9, 4.0, 1.9)
    ax.text(3.55, 2.2, "O(|U| + Σ|Sᵢ|)", ha="center", fontsize=8.5, color="#475569")
    for i, y in enumerate(ys.values(), start=1):
        caja(ax, 5.0, y, 1.5, 0.55, f"nodo {i}\ncᵢ = 0", "#eff4ff", AZUL, 8.5)
    caja(ax, 8.1, 1.9, 3.4, 2.4, "Utilidad conjunta\nf(A) = | ∪ᵢ∈A Sᵢ |\n\nmismo cupo k,\nmismo umbral t,\nP = 0", "#fff", TINTA, 9)
    for y in ys.values():
        flecha(ax, 5.75, y, 6.4, 1.9 + (y - 1.9) * 0.35)
    guardar(fig, "fig05_reduccion_cobertura.png")


def reduccion_dominante():
    pos = {0: (0, 1.2), 1: (1, 2), 2: (1, 0.4), 3: (2.2, 1.2), 4: (3.2, 2), 5: (3.2, 0.4)}
    E = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]
    D = {0, 3}
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.7))
    for ax, titulo, pesos in [(axs[0], "Grafo G y conjunto dominante D = {1, 4}", False),
                              (axs[1], "Caso construido: aᵥ = 1, wᵤᵥ = 1 en las aristas", True)]:
        ax.axis("off"); ax.set_xlim(-0.5, 3.7); ax.set_ylim(-0.45, 2.6); ax.set_aspect("equal")
        ax.set_title(titulo, fontsize=10)
        for u, v in E:
            (x1, y1), (x2, y2) = pos[u], pos[v]
            ax.plot([x1, x2], [y1, y2], color=AZUL if pesos else "#94a3b8", lw=2.2 if pesos else 1.3)
            if pesos:
                ax.text((x1 + x2) / 2, (y1 + y2) / 2, "1", fontsize=8, ha="center", va="center",
                        bbox=dict(fc="white", ec="none", pad=0.5))
        for v, (x, y) in pos.items():
            elegido = v in D
            ax.add_patch(Circle((x, y), 0.22, fc=AZUL if (pesos or elegido) else "white",
                                ec=TINTA, lw=2.4 if elegido else 1.1, alpha=1 if elegido or not pesos else 0.55))
            ax.text(x, y, str(v + 1), ha="center", va="center", fontsize=10,
                    color="white" if (pesos or elegido) else TINTA, fontweight="bold")
    axs[1].text(1.6, -0.25, "f(D) = |N[D]| = 6 = |V|  ⇔  D domina a todos", ha="center", fontsize=9)
    guardar(fig, "fig06_reduccion_dominante.png")


# ---------------------------------------------------------------------------
def caso_15():
    ruta = os.path.join(RAIZ, "resultados", "casos", "entrada_G2_red_15_nodos", "resultado.json")
    with open(ruta, encoding="utf-8") as fh:
        contenido = json.load(fh)
    res, caso = contenido["resultado"], leer_caso_red(contenido["entrada"])
    r1 = res["rondas"][0]

    fig, ax = plt.subplots(figsize=(8, 3.8))
    traza = r1["traza_seleccion"]
    etiquetas = [f"{p['paso']}\n{p['nodo']}" for p in traza]
    ax.bar(etiquetas, [p["ganancia_marginal"] for p in traza], color=AZUL, label="ganancia del paso Δ")
    for i, p in enumerate(traza):
        g = p["ganancia_marginal"]
        dentro = g > 30          # en barras altas el número va adentro, para no chocar con la línea
        ax.text(i, g - 9 if dentro else g + 2, f"{g:.2f}", ha="center", fontsize=8.5,
                color="white" if dentro else TINTA)
    ax.plot(etiquetas, [p["utilidad_acumulada"] for p in traza], "o-", color=NARANJA, label="f(S) acumulada")
    ax.axhline(r1["optimo"]["valor"], color=VERDE, ls="--", lw=1.4, label=f"óptimo {r1['optimo']['valor']:.2f}")
    ax.set_ylabel("utilidad"); ax.set_xlabel("paso del voraz y nodo elegido"); ax.legend(frameon=False, fontsize=8.5)
    ax.set_title("Caso de 15 nodos: selección de cada ronda")
    guardar(fig, "fig07_caso15_seleccion.png")

    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    nodos = [p["nodo"] for p in res["presupuesto_usado"]]
    base = [0] * len(nodos)
    for r, c in zip(res["rondas"], [AZUL, NARANJA, VERDE]):
        rec = {f["nodo"]: f["unidades"] for f in r["reparto"]}
        h = [rec.get(n, 0) for n in nodos]
        ax.bar(nodos, h, bottom=base, color=c, label=f"ronda {r['ronda']}")
        base = [b + x for b, x in zip(base, h)]
    ax.axhline(18, color=ROJO, ls="--", lw=1.4); ax.text(-0.4, 18.4, "tope Rᵢ = 18", color=ROJO, fontsize=8.5)
    ax.set_ylim(0, 21); ax.set_ylabel("unidades de ruido"); ax.legend(frameon=False, fontsize=8.5, ncol=3, loc="upper left",
                                                                     bbox_to_anchor=(0.12, 1.0))
    ax.set_title("Caso de 15 nodos: presupuesto usado por nodo en las 3 rondas")
    guardar(fig, "fig08_caso15_presupuesto.png")

    S = [caso.ids.index(n) for n in r1["seleccion"]]
    filas = [[caso.W[u][v] for v in range(caso.N)] for u in S]
    prob = []
    for v in range(caso.N):
        q = 1.0
        for u in S:
            q *= 1 - caso.W[u][v]
        prob.append(1 - q)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    im = ax.imshow(filas + [prob], cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(caso.N), caso.ids, rotation=45, fontsize=8)
    ax.set_yticks(range(len(S) + 1), [caso.ids[u] for u in S] + ["p influido"], fontsize=8.5)
    ax.axhline(len(S) - 0.5, color="white", lw=3)
    for c in range(caso.N):
        ax.text(c, len(S), f"{prob[c]:.2f}", ha="center", va="center", fontsize=6.5,
                color="white" if prob[c] > 0.6 else TINTA)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01, label="peso w")
    ax.set_title("Caso de 15 nodos: influencia de los participantes sobre cada nodo")
    for s in ax.spines.values():
        s.set_visible(False)
    guardar(fig, "fig09_caso15_influencia.png")


if __name__ == "__main__":
    print(f"Figuras en {SALIDA}")
    flujo_ronda(); grafo_ejemplo(); utilidad_concava(); nivel_agua()
    reduccion_cobertura(); reduccion_dominante(); caso_15()
