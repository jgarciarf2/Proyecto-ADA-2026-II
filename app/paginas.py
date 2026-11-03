"""
Las cuatro páginas de la interfaz. Cada función dibuja una página completa.
"""
import glob
import json
import os

import pandas as pd
import streamlit as st

from ada.casos import CasoInvalido, caso_sintetico
from app.estilos import aviso, encabezado, nota
from app.vista_resultado import mostrar
from experimentos.casos import CARPETA_EJEMPLOS, ejecutar_caso, guardar_evidencia
from experimentos.comun import RAIZ

CARPETA_EVIDENCIAS = os.path.join(RAIZ, "resultados", "casos")


@st.cache_data(show_spinner=False)
def _resolver(texto_json, con_optimo):
    """Se cachea por el texto del caso: volver a una página no repite el cálculo."""
    datos = json.loads(texto_json)
    return datos, ejecutar_caso(datos, con_optimo=con_optimo)


def _resolver_seguro(texto, nombre, con_optimo):
    try:
        datos = json.loads(texto)
        datos.setdefault("nombre", nombre)
        return _resolver(json.dumps(datos, sort_keys=True), con_optimo)
    except json.JSONDecodeError as e:
        st.error(f"El archivo no es un JSON válido: {e}")
    except CasoInvalido as e:
        st.error(f"El caso no es válido: {e}")
    return None, None


# ---------------------------------------------------------------------------
def cargar_caso():
    encabezado("Cargar caso", "Sube un caso en JSON o elige uno de ejemplo. Se resuelve en el momento con la "
                              "solución base: selección voraz y reparto óptimo.", "archivo")
    ejemplos = sorted(glob.glob(os.path.join(CARPETA_EJEMPLOS, "*.json")))
    izq, der = st.columns([1.4, 1], gap="large")
    with izq:
        archivo = st.file_uploader("Archivo del caso (.json)", type=["json"])
    with der:
        nombres = ["Ninguno"] + [os.path.splitext(os.path.basename(e))[0] for e in ejemplos]
        elegido = st.selectbox("O usa un caso de ejemplo", nombres, index=1 if len(nombres) > 1 else 0,
                               disabled=archivo is not None)
        con_optimo = st.toggle("Comparar con el óptimo", value=True,
                               help="Calcula el óptimo por fuerza bruta, solo si C(N, k) ≤ 200 000. Si no, se muestra el techo que da la cota (1−1/e).")

    if archivo is not None:
        texto, nombre = archivo.getvalue().decode("utf-8"), os.path.splitext(archivo.name)[0]
    elif elegido != "Ninguno":
        nombre = elegido
        with open(os.path.join(CARPETA_EJEMPLOS, f"{elegido}.json"), encoding="utf-8") as fh:
            texto = fh.read()
    else:
        aviso("Sube un archivo o elige un ejemplo para ver el resultado.")
        return

    datos, res = _resolver_seguro(texto, nombre, con_optimo)
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
        opt = r["optimo"]["valor"] if r["optimo"] else None
        filas.append({"Caso": r["caso"], "N": r["N"], "k": r["k"], "B": r["B"],
                      "f(S)": round(r["utilidad_conjunta"], 3),
                      "f(S) / óptimo": f"{r['utilidad_conjunta'] / opt:.4f}" if opt else "—",
                      "U(x)": round(r["utilidad_reparto"], 3),
                      "Tiempo (ms)": round(r["tiempo_s"]["total"] * 1e3, 3),
                      "Restricciones": "cumple" if r["cumple_todo"] else "NO cumple"})
    return filas, todos


def evidencias():
    encabezado("Evidencias", "Casos ya ejecutados con su resultado, tiempo y traza. Selecciona una fila "
                             "para ver el detalle.", "carpeta")
    aviso("Para generar o actualizar la evidencia de una carpeta de casos, desde la raíz del proyecto:<br>"
          "<code>python -m experimentos.casos casos/ejemplos</code>", icono="terminal")
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
def modo_demo():
    encabezado("Modo demo", "Instancias sintéticas para explicar el algoritmo en vivo: mueve los controles "
                            "y mira cómo cambian la selección y el reparto.", "controles")
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        N = st.slider("Nodos candidatos (N)", 5, 80, 14)
        k = st.slider("Cupo de la ronda (k)", 1, N - 1, min(4, N - 1))
    with c2:
        M = st.slider("Tipos de datos (M)", 5, 200, 30)
        d = st.slider("Tipos por nodo (d)", 1, min(20, M), min(5, M))
    with c3:
        B = st.slider("Presupuesto (B)", 0, 300, 20)
        semilla = st.number_input("Semilla", 0, 10_000, 7, step=1)
    datos = caso_sintetico(f"demo_N{N}_k{k}_B{B}", N, M, d, k, B, int(semilla))
    _, res = _resolver(json.dumps(datos, sort_keys=True), True)
    st.divider()
    mostrar(datos, res, clave="demo")


# ---------------------------------------------------------------------------
def experimentos():
    encabezado("Experimentos", "Tiempo medido contra la función de eficiencia teórica. Se generan con "
                               "python -m experimentos.parte1 y python -m experimentos.parte2.", "grafica")
    p1, p2 = st.tabs(["Parte 1: reparto", "Parte 2: selección"])
    with p1:
        _figura("parte1/variaN.png", "Tiempo al variar N con B fijo",
                "Izquierda: tiempo medido y la curva c₁·N + c₂·B·log₂N ajustada. Derecha: medido / predicho.")
        _figura("parte1/variaB.png", "Tiempo al variar B con N fijo", "El crecimiento en B es lineal, como predice T(N, B).")
        _figura("parte1/conteo.png", "Comparaciones del montículo contra la cota",
                "Conteo exacto, independiente de la máquina: heapify ≈ 1.65·N y pasos ≈ 1.1·B·log₂N, por debajo de 2.")
    with p2:
        _figura("parte2/cota.png", "Calidad del voraz frente al óptimo",
                "500 instancias pequeñas: todas quedan por encima de la garantía 1 − 1/e ≈ 0.632.")
        _figura("parte2/variaN.png", "Tiempo del voraz al variar N (k = 20)", "Crecimiento lineal en N, como O(N·k·d).")
        _figura("parte2/variak.png", "Tiempo del voraz al variar k (N = 2000)", "Crecimiento lineal en k.")
        _figura("parte2/voraz_vs_fb.png", "Voraz contra fuerza bruta",
                "La fuerza bruta crece exponencialmente (recta en escala log); el voraz se queda por debajo de 1 ms.")


def _figura(ruta, titulo, texto):
    completa = os.path.join(RAIZ, "resultados", ruta)
    st.markdown(f"**{titulo}**")
    nota(texto)
    if os.path.exists(completa):
        st.image(completa, width="stretch")
    else:
        nota(f"No existe resultados/{ruta}: corre el experimento correspondiente.")
    st.write("")
