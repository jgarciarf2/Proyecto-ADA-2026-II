"""
Páginas Cargar caso y Evidencias (el modo demo está en app/demo.py y los experimentos en
app/pagina_experimentos.py). Cada función dibuja una página completa.
"""
import glob
import json
import os

import pandas as pd
import streamlit as st

from ada.casos import CasoInvalido
from app.estilos import aviso, encabezado, nota
from app.vista_resultado import mostrar
from experimentos.casos import CARPETA_EJEMPLOS, ejecutar_caso, fila_resumen, guardar_evidencia
from experimentos.comun import RAIZ

CARPETA_EVIDENCIAS = os.path.join(RAIZ, "resultados", "casos")
CARPETA_PROFESORA = os.path.join(RAIZ, "casos", "profesora")


SELECCION_UI = {"Voraz por ganancia (solución base)": "ganancia", "Algoritmo A · V1 (razón + mejor nodo)": "A",
                "Algoritmo B · V1 (enumeración parcial)": "B"}


@st.cache_data(show_spinner=False)
def _resolver(texto_json, con_optimo, seleccion="ganancia"):
    """Se cachea por el texto del caso: volver a una página no repite el cálculo."""
    datos = json.loads(texto_json)
    return datos, ejecutar_caso(datos, con_optimo=con_optimo, seleccion=seleccion)


def _resolver_seguro(texto, nombre, con_optimo, seleccion="ganancia"):
    try:
        datos = json.loads(texto)
        datos.setdefault("nombre", nombre)
        return _resolver(json.dumps(datos, sort_keys=True), con_optimo, seleccion)
    except json.JSONDecodeError as e:
        st.error(f"El archivo no es un JSON válido: {e}")
    except CasoInvalido as e:
        st.error(f"El caso no es válido: {e}")
    except ValueError as e:                     # por ejemplo, el algoritmo B con un caso demasiado grande
        st.error(f"No se pudo resolver con ese algoritmo: {e}")
    return None, None


# ---------------------------------------------------------------------------
def cargar_caso():
    encabezado("Cargar caso", "Sube un caso en JSON o elige uno guardado. Se resuelve en el momento con el "
                              "algoritmo de selección que elijas y el reparto óptimo.", "archivo")
    # primero los casos de la profesora, después los ejemplos sintéticos
    rutas = (sorted(glob.glob(os.path.join(CARPETA_PROFESORA, "*.json")))
             + sorted(glob.glob(os.path.join(CARPETA_EJEMPLOS, "*.json"))))
    etiquetas = {f"{os.path.basename(os.path.dirname(r))} / {os.path.splitext(os.path.basename(r))[0]}": r
                 for r in rutas}
    izq, der = st.columns([1.4, 1], gap="large")
    with izq:
        archivo = st.file_uploader("Archivo del caso (.json)", type=["json"])
    with der:
        nombres = ["Ninguno"] + list(etiquetas)
        elegido = st.selectbox("O usa un caso guardado", nombres, index=1 if len(nombres) > 1 else 0,
                               disabled=archivo is not None)
        etiqueta = st.selectbox("Algoritmo de selección", list(SELECCION_UI),
                                help="Solo para casos con el formato de la profesora. A y B son los algoritmos "
                                     "de la variante V1 (docs/03_variantes.md); B solo admite N ≤ 50.")
        con_optimo = st.toggle("Comparar con el óptimo", value=True,
                               help="Calcula el óptimo por fuerza bruta solo si hay pocos subconjuntos por revisar "
                                    "(≤ 200 000). Si no, se muestra el techo que da la cota (1−1/e).")

    if archivo is not None:
        texto, nombre = archivo.getvalue().decode("utf-8"), os.path.splitext(archivo.name)[0]
    elif elegido != "Ninguno":
        nombre = os.path.splitext(os.path.basename(etiquetas[elegido]))[0]
        with open(etiquetas[elegido], encoding="utf-8") as fh:
            texto = fh.read()
    else:
        aviso("Sube un archivo o elige un ejemplo para ver el resultado.")
        return

    datos, res = _resolver_seguro(texto, nombre, con_optimo, SELECCION_UI[etiqueta])
    if res is None:
        return
    st.divider()
    mostrar(datos, res, clave="cargar")
    st.divider()
    if st.button("Guardar como evidencia", type="primary"):
        destino = os.path.join(CARPETA_EVIDENCIAS, res["caso"])
        guardar_evidencia(datos, res, destino)
        st.success(f"Guardado en resultados/casos/{res['caso']}/")


# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _leer_evidencias(_marca):
    filas, todos = [], {}
    for ruta in sorted(glob.glob(os.path.join(CARPETA_EVIDENCIAS, "*", "resultado.json"))):
        with open(ruta, encoding="utf-8") as fh:
            contenido = json.load(fh)
        r = contenido["resultado"]
        todos[r["caso"]] = contenido
        f = fila_resumen(r)          # mismas columnas para los dos formatos (en red se suman las rondas)
        filas.append({"Caso": f["caso"], "Rondas": f["rondas"], "N": f["N"], "k": f["k"], "B": f["B"],
                      "f(S)": f["f(S)"],
                      "f(S) / óptimo": _razon(f["f(S)"], f["optimo_f"]),
                      "U(x)": f["U(x)"], "Tiempo (ms)": f["t_total_ms"],
                      "Restricciones": "cumple" if f["cumple_restricciones"] else "NO cumple"})
    return filas, todos


def _razon(valor, optimo):
    """f(S)/óptimo como texto. Sin óptimo calculado: "—". Óptimo 0 (nadie pudo participar): 1 si f(S) también es 0."""
    if optimo == "":
        return "—"
    if optimo == 0:
        return "1.0000" if valor == 0 else "—"
    return f"{valor / optimo:.4f}"


def evidencias():
    encabezado("Evidencias", "Casos ya ejecutados con su resultado, tiempo y traza. Selecciona una fila "
                             "para ver el detalle.", "carpeta")
    aviso("Para generar o actualizar la evidencia de una carpeta de casos, desde la raíz del proyecto:<br>"
          "<code>python -m experimentos.casos casos/profesora</code>", icono="terminal")
    marca = max((os.path.getmtime(p) for p in glob.glob(os.path.join(CARPETA_EVIDENCIAS, "*", "resultado.json"))),
                default=0)
    filas, todos = _leer_evidencias(marca)
    if not filas:
        nota("Todavía no hay evidencias guardadas.")
        return
    seleccion = st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch",
                             on_select="rerun", selection_mode="single-row", key="tabla-evidencias")
    filas_sel = seleccion.selection.rows
    if not filas_sel:
        nota("Selecciona un caso en la tabla para ver su detalle.")
        return
    contenido = todos[filas[filas_sel[0]]["Caso"]]
    st.divider()
    mostrar(contenido["entrada"], contenido["resultado"], clave="evid")


# ---------------------------------------------------------------------------
