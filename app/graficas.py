"""
Gráficas del resultado de un caso (Plotly). Reciben el caso ya leído (ada.casos.Caso)
y el resultado serializado (ada.casos.resultado_a_dict).
"""
import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.estilos import AZUL, GRIS, NARANJA, ROJO, VERDE, etiqueta_nodo

COTA = 1 - 1 / math.e
FUENTE = dict(family="Source Sans Pro, sans-serif", size=12, color="#334155")


def _base(fig, alto, margen_der=20):
    fig.update_layout(height=alto, margin=dict(l=10, r=margen_der, t=30, b=10), font=FUENTE,
                      plot_bgcolor="white", paper_bgcolor="white", bargap=0.25,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
                      hoverlabel=dict(font_size=12))
    fig.update_xaxes(showgrid=False, linecolor="#94a3b8", ticks="outside", tickcolor="#cbd5e1", automargin=True)
    fig.update_yaxes(gridcolor="#eef2f6", zeroline=False, automargin=True)
    return fig


def seleccion(res, con_garantia=True):
    """
    Ganancia de cada paso (barras, eje izquierdo) y utilidad acumulada con el óptimo y la
    garantía (eje derecho). Con dos ejes las barras se ven aunque k sea grande y la
    acumulada sea mucho mayor que cada ganancia. con_garantia=False cuando hay costos de
    participación: ahí la cota (1 − 1/e) no aplica tal cual y solo se dibuja el óptimo.
    """
    traza = res["traza_seleccion"]
    etiquetas = [f"{p['paso']} · {p['nodo']}" for p in traza]
    ganancias = [p["ganancia_marginal"] for p in traza]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=etiquetas, y=ganancias, name="ganancia del paso", marker_color=AZUL, opacity=0.85,
                customdata=[[p["nodo"], p["candidatos_evaluados"]] for p in traza],
                hovertemplate="paso %{x}<br>nodo %{customdata[0]}<br>ganancia %{y:.3f}"
                              "<br>candidatos evaluados %{customdata[1]}<extra></extra>", secondary_y=False)
    fig.add_scatter(x=etiquetas, y=[p["utilidad_acumulada"] for p in traza], name="utilidad acumulada",
                    mode="lines+markers", line=dict(color=NARANJA, width=2.5),
                    marker=dict(size=7, color="white", line=dict(color=NARANJA, width=2)),
                    hovertemplate="acumulada %{y:.3f}<extra></extra>", secondary_y=True)
    # Las barras ocupan como mucho el 45 % inferior y la garantía queda en el 55 %: así los
    # textos de las líneas (a la izquierda, donde la acumulada todavía va baja) no chocan.
    if res["optimo"]:
        opt = res["optimo"]["valor"]
        _linea(fig, opt, VERDE, f"óptimo {opt:.2f}")
        if con_garantia:
            _linea(fig, COTA * opt, ROJO, f"garantía {COTA * opt:.2f}")
        techo = opt
    elif con_garantia:
        techo = res["utilidad_conjunta"] / COTA
        _linea(fig, techo, ROJO, f"techo {techo:.2f}")
    else:
        techo = res["utilidad_conjunta"]
    fig.update_xaxes(title_text="paso · nodo elegido", type="category")
    fig.update_yaxes(title_text="ganancia del paso", range=[0, max(ganancias, default=1) * 2.2],
                     secondary_y=False)
    fig.update_yaxes(title_text="utilidad acumulada", range=[0, techo * 1.14], showgrid=False,
                     secondary_y=True)
    return _base(fig, 380)


def _linea(fig, y, color, texto):
    """Línea horizontal en el eje derecho (y2) con su texto encima, pegado a la izquierda."""
    fig.add_shape(type="line", xref="paper", x0=0, x1=1, yref="y2", y0=y, y1=y,
                  line=dict(color=color, dash="dash", width=1.5))
    fig.add_annotation(xref="paper", x=0.01, yref="y2", y=y, text=texto, showarrow=False,
                       xanchor="left", yanchor="bottom", font=dict(color=color, size=11),
                       bgcolor="rgba(255,255,255,.85)")


def cobertura(caso, res):
    """Filas = nodos elegidos (en orden), columnas = tipos cubiertos. 1 = lo cubre solo él, 2 = repetido."""
    pos = {str(i): n for n, i in enumerate(caso.ids)}
    elegidos = [pos[str(i)] for i in res["seleccion"]]
    cuenta = {}
    for n in elegidos:
        for e in caso.conjuntos[n]:
            cuenta[e] = cuenta.get(e, 0) + 1
    tipos = sorted(cuenta)
    z = [[(2 if cuenta[e] > 1 else 1) if e in caso.conjuntos[n] else 0 for e in tipos] for n in elegidos]
    texto = [[f"{etiqueta_nodo(caso.ids[n])} · tipo {e} · peso {caso.pesos[e]:.2f}"
              + (" · repetido" if cuenta[e] > 1 and e in caso.conjuntos[n] else "") for e in tipos]
             for n in elegidos]
    escala = [[0, "#f1f5f9"], [0.33, "#f1f5f9"], [0.34, AZUL], [0.66, AZUL], [0.67, NARANJA], [1, NARANJA]]
    fig = go.Figure(go.Heatmap(z=z, x=[str(e) for e in tipos], y=[etiqueta_nodo(caso.ids[n]) for n in elegidos],
                               zmin=0, zmax=2, colorscale=escala, showscale=False, xgap=2 if len(tipos) <= 60 else 0,
                               ygap=3, text=texto, hovertemplate="%{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(title_text=f"tipos cubiertos ({len(tipos)}/{caso.M})", type="category",
                     showticklabels=len(tipos) <= 40)
    alto = max(260, min(560, 70 + 30 * len(elegidos)))
    return _base(fig, alto), len(tipos), sum(1 for c in cuenta.values() if c > 1)


def reparto(caso, res, max_por_nodo=30, extra=3):
    """
    Nivel de agua: para cada nodo elegido, una barra por unidad con su ganancia marginal.
    Azul = entregada, gris = la siguiente que no se entregó. Si un nodo recibió muchas
    unidades se muestran solo las últimas max_por_nodo.
    """
    pos = {str(i): n for n, i in enumerate(caso.ids)}
    fig = go.Figure()
    centros, nombres, x0 = [], [], 0
    xs_e, ys_e, hov_e, xs_n, ys_n, hov_n = [], [], [], [], [], []
    ultimas, siguientes = [], []
    for fila in res["reparto"]:
        n, x = pos[str(fila["nodo"])], fila["unidades"]
        u = caso.utilidades[n]
        desde = max(1, x - max_por_nodo + 1)
        unidades = list(range(desde, x + extra + 1))
        for j, t in enumerate(unidades):
            g = u.marginal(t - 1)
            if g <= 0:
                continue
            destino = (xs_e, ys_e, hov_e) if t <= x else (xs_n, ys_n, hov_n)
            destino[0].append(x0 + j)
            destino[1].append(g)
            destino[2].append(f"{etiqueta_nodo(fila['nodo'])} · unidad {t} · ganancia {g:.4f}")
        if x > 0:
            ultimas.append(u.marginal(x - 1))
        if u.marginal(x) > 0:
            siguientes.append(u.marginal(x))
        centros.append(x0 + (len(unidades) - 1) / 2)
        nombres.append(f"{etiqueta_nodo(fila['nodo'])}<br><b>{x} unid.</b>")
        x0 += len(unidades) + 2
    fig.add_bar(x=xs_e, y=ys_e, name="unidad entregada", marker_color=AZUL, text=hov_e,
                hovertemplate="%{text}<extra></extra>", textposition="none")
    fig.add_bar(x=xs_n, y=ys_n, name="siguiente unidad (no entregada)", marker_color=GRIS, text=hov_n,
                hovertemplate="%{text}<extra></extra>", textposition="none")
    nivel = min(ultimas) if ultimas else None
    if nivel is not None:
        fig.add_hline(y=nivel, line=dict(color=NARANJA, dash="dash", width=2),
                      annotation=dict(text=f"nivel λ = {nivel:.4f}", font=dict(color=NARANJA, size=11),
                                      bgcolor="rgba(255,255,255,.85)"),
                      annotation_position="top right")
    todos = ys_e + ys_n
    log = bool(todos) and max(todos) / min(todos) > 30
    fig.update_yaxes(title_text="ganancia marginal" + (" (escala log)" if log else ""),
                     type="log" if log else "linear")
    # espacio vacío a la derecha para que el texto del nivel no quede encima de las barras
    fig.update_xaxes(tickvals=centros, ticktext=nombres, range=[-1.5, max(x0 - 1, 1) + max(6, x0 * 0.12)])
    fig.update_layout(barmode="overlay", bargap=0.15)
    return _base(fig, 400), nivel, (max(siguientes) if siguientes else None)


def influencia(ids, W, seleccion):
    """
    Filas = nodos elegidos (en orden), columnas = todos los nodos; el color es el peso de
    influencia w_uv (1 en la diagonal). La última fila es la probabilidad de que cada
    nodo quede influido por S: 1 − Π_{u∈S}(1 − w_uv).
    """
    pos = {str(i): n for n, i in enumerate(ids)}
    S = [pos[str(i)] for i in seleccion]
    z = [[W[u][v] for v in range(len(ids))] for u in S]
    prob = []
    for v in range(len(ids)):
        q = 1.0
        for u in S:
            q *= 1.0 - W[u][v]
        prob.append(1.0 - q)
    filas = [etiqueta_nodo(ids[u]) for u in S] + ["influido por S"]
    columnas = [etiqueta_nodo(i) for i in ids]
    texto = [[f"{filas[r]} → {columnas[c]} · peso {z[r][c]:.2f}" for c in range(len(ids))] for r in range(len(S))]
    texto.append([f"{columnas[c]} · probabilidad de quedar influido {prob[c]:.3f}" for c in range(len(ids))])
    escala = [[0, "#f1f5f9"], [0.5, "#93b4f5"], [1, AZUL]]
    fig = go.Figure(go.Heatmap(z=z + [prob], x=columnas, y=filas, zmin=0, zmax=1, colorscale=escala,
                               xgap=2, ygap=3, text=texto, hovertemplate="%{text}<extra></extra>",
                               colorbar=dict(title=dict(text="peso", side="right"), thickness=10, len=0.8)))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(type="category", tickangle=-45)
    return _base(fig, max(280, 90 + 34 * (len(S) + 1)))


def presupuesto_por_nodo(uso, rondas):
    """Barras apiladas: unidades que recibió cada nodo en cada ronda, con la línea del tope por nodo."""
    nodos = [p["nodo"] for p in uso]
    tonos = [AZUL, NARANJA, VERDE, "#8b5cf6", "#0891b2", "#be185d"]
    fig = go.Figure()
    for j, r in enumerate(rondas):
        recibido = {fila["nodo"]: fila["unidades"] for fila in r["reparto"]}
        fig.add_bar(x=[etiqueta_nodo(n) for n in nodos], y=[recibido.get(n, 0) for n in nodos],
                    name=f"ronda {r['ronda']}", marker_color=tonos[j % len(tonos)],
                    hovertemplate=f"ronda {r['ronda']}<br>%{{x}}: %{{y}} unidades<extra></extra>")
    tope = max(p["tope"] for p in uso)
    fig.add_shape(type="line", xref="paper", x0=0, x1=1, y0=tope, y1=tope,
                  line=dict(color=ROJO, dash="dash", width=1.5))
    fig.add_annotation(xref="paper", x=0.01, y=tope, text=f"tope por nodo = {tope}", showarrow=False,
                       xanchor="left", yanchor="bottom", font=dict(color=ROJO, size=11),
                       bgcolor="rgba(255,255,255,.85)")
    fig.update_layout(barmode="stack", legend_traceorder="normal")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="unidades de presupuesto", range=[0, tope * 1.18])
    return _base(fig, 340)
