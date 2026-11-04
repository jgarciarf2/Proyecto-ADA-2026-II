"""
Colores, íconos SVG (sin emojis) y piezas de HTML reutilizables de la interfaz.
"""
from urllib.parse import quote

import streamlit as st

AZUL = "#2563eb"
NARANJA = "#ea7a2b"
VERDE = "#16a34a"
ROJO = "#dc2626"
GRIS = "#cbd2dc"
TEXTO_2 = "#64748b"
BORDE = "#e2e8f0"

# Trazos de 24x24 con stroke="currentColor": toman el color del texto que los rodea.
_TRAZOS = {
    "red": '<circle cx="5" cy="12" r="2.2"/><circle cx="19" cy="5" r="2.2"/><circle cx="19" cy="19" r="2.2"/>'
           '<path d="M7 11l10-5M7 13l10 5"/>',
    "archivo": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>'
               '<path d="M12 18v-6"/><path d="M9 15l3-3 3 3"/>',
    "carpeta": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
               '<path d="M8 13h8"/>',
    "controles": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/>'
                 '<circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "grafica": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "objetivo": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
    "capas": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "reloj": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "escudo": '<path d="M12 3L5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "check": '<path d="M5 12l4 4 10-10"/>',
    "equis": '<path d="M6 6l12 12M18 6L6 18"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M13 15h4"/>',
}


def svg(nombre, tam=18, color="currentColor"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'style="flex-shrink:0">{_TRAZOS[nombre]}</svg>')


def _mascara(nombre):
    """El ícono como data URI para usarlo de máscara en CSS (así toma el color del enlace)."""
    s = svg(nombre, 24, "black")
    return f'url("data:image/svg+xml,{quote(s)}")'


# Íconos de la navegación lateral, en el mismo orden de las páginas de principal.py
ICONOS_NAV = ["archivo", "carpeta", "controles", "grafica"]


def aplicar_estilos():
    reglas_nav = "".join(
        f'[data-testid="stSidebarNavItems"] li:nth-child({i + 1}) a::before{{'
        f'-webkit-mask-image:{_mascara(n)};mask-image:{_mascara(n)};}}'
        for i, n in enumerate(ICONOS_NAV))
    st.markdown(f"""<style>
.block-container {{padding-top:2.2rem; padding-bottom:3rem; max-width:1250px;}}
[data-testid="stSidebarNavItems"] a {{gap:.6rem; align-items:center;}}
[data-testid="stSidebarNavItems"] a::before {{
  content:""; width:18px; height:18px; flex:0 0 18px; background-color:currentColor;
  -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat; -webkit-mask-size:contain; mask-size:contain;}}
{reglas_nav}
.ada-encabezado {{display:flex; gap:.8rem; align-items:flex-start; margin:0 0 1.2rem 0;}}
.ada-encabezado .ada-ico {{color:{AZUL}; background:#eff4ff; border-radius:10px; padding:8px; display:flex;}}
.ada-encabezado h1 {{font-size:1.55rem; line-height:1.25; margin:0; padding:0;}}
.ada-encabezado p {{color:{TEXTO_2}; margin:.2rem 0 0 0; font-size:.92rem;}}
.ada-metricas {{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:.8rem; margin:.4rem 0 1.1rem 0;}}
.ada-metrica {{border:1px solid {BORDE}; border-radius:12px; padding:.85rem 1rem; background:#fff; min-width:0;}}
.ada-metrica .t {{display:flex; gap:.45rem; align-items:center; color:{TEXTO_2}; font-size:.8rem;}}
.ada-metrica .v {{font-size:1.6rem; font-weight:650; line-height:1.3; margin-top:.25rem;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}}
.ada-metrica .s {{color:{TEXTO_2}; font-size:.78rem; line-height:1.35; margin-top:.15rem;}}
.ada-nota {{color:{TEXTO_2}; font-size:.84rem; line-height:1.45; margin:.1rem 0 .4rem 0;}}
.ada-chips {{display:flex; flex-wrap:wrap; gap:.45rem; margin:.3rem 0 .2rem 0;}}
.ada-chip {{display:inline-flex; gap:.35rem; align-items:center; border-radius:999px; padding:.28rem .7rem;
  font-size:.8rem; line-height:1.2;}}
.ada-chip.ok {{background:#e9f7ef; color:#15803d;}}
.ada-chip.no {{background:#fdecec; color:{ROJO};}}
.ada-aviso {{display:flex; gap:.6rem; align-items:flex-start; border:1px solid {BORDE}; background:#f8fafc;
  border-radius:12px; padding:.8rem 1rem; color:#334155; font-size:.88rem; line-height:1.45; margin:.4rem 0 1.6rem 0;}}
.ada-aviso code {{font-size:.82rem;}}
.ada-marca {{display:flex; gap:.6rem; align-items:center; padding:.2rem 0 .9rem 0;}}
.ada-marca .n {{font-weight:700; font-size:1rem; line-height:1.2;}}
.ada-marca .g {{color:{TEXTO_2}; font-size:.78rem;}}
</style>""", unsafe_allow_html=True)


def encabezado(titulo, subtitulo, icono):
    st.markdown(f'<div class="ada-encabezado"><div class="ada-ico">{svg(icono, 22)}</div>'
                f'<div><h1>{titulo}</h1><p>{subtitulo}</p></div></div>', unsafe_allow_html=True)


def marca_lateral():
    """Logo arriba de la navegación: un SVG con el ícono de red y el nombre del proyecto."""
    logo = (f'<svg xmlns="http://www.w3.org/2000/svg" width="190" height="40" viewBox="0 0 190 40">'
            f'<g transform="translate(2,7) scale(1.1)" fill="none" stroke="{AZUL}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{_TRAZOS["red"]}</g>'
            f'<text x="38" y="18" font-family="Segoe UI, Arial, sans-serif" font-size="15" font-weight="700" '
            f'fill="#0f172a">Proyecto Red</text>'
            f'<text x="38" y="33" font-family="Segoe UI, Arial, sans-serif" font-size="11" '
            f'fill="{TEXTO_2}">ADA 2026-2 · Grupo 2</text></svg>')
    st.logo(f"data:image/svg+xml,{quote(logo)}", size="large")


def etiqueta_nodo(ident):
    """Los ids numéricos se muestran como 'nodo 7'; los de texto ('n7') tal cual."""
    return f"nodo {ident}" if isinstance(ident, int) else str(ident)


def metricas(lista):
    """lista de (icono, titulo, valor, subtitulo, color_valor)."""
    tarjetas = "".join(
        f'<div class="ada-metrica"><div class="t">{svg(i, 15)}<span>{t}</span></div>'
        f'<div class="v" style="color:{c}" title="{v}">{v}</div><div class="s">{s}</div></div>'
        for i, t, v, s, c in lista)
    st.markdown(f'<div class="ada-metricas">{tarjetas}</div>', unsafe_allow_html=True)


def nota(texto):
    st.markdown(f'<div class="ada-nota">{texto}</div>', unsafe_allow_html=True)


def aviso(texto, icono="info"):
    st.markdown(f'<div class="ada-aviso"><span style="color:{AZUL};padding-top:1px">{svg(icono, 18)}</span>'
                f'<div>{texto}</div></div>', unsafe_allow_html=True)


_NOMBRES_RESTRICCION = {
    "|S| <= k": "|S| ≤ k",
    "sin nodos repetidos": "sin nodos repetidos",
    "nodos validos (0..N-1)": "nodos válidos (0..N−1)",
    "sum x_i <= B": "Σ xᵢ ≤ B",
    "x_i entero >= 0": "xᵢ entero ≥ 0",
    "costo de participacion <= P": "Σ cᵢ ≤ P",
    "x_i <= presupuesto restante": "xᵢ ≤ presupuesto restante",
    "presupuesto total por nodo": "uso total ≤ tope de cada nodo",
}


def chips_verificacion(verificaciones):
    """Una etiqueta por restricción; al pasar el mouse se ve el detalle (por ejemplo, Σ xᵢ = 20, B = 20)."""
    chips = "".join(
        f'<span class="ada-chip {"ok" if v["cumple"] else "no"}" title="{v["detalle"]}">'
        f'{svg("check" if v["cumple"] else "equis", 14)}'
        f'{_NOMBRES_RESTRICCION.get(v["restriccion"], v["restriccion"])}</span>'
        for v in verificaciones)
    st.markdown(f'<div class="ada-chips">{chips}</div>', unsafe_allow_html=True)
