"""
Punto de entrada de la interfaz.  Uso (desde la raíz):  streamlit run app/principal.py
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import streamlit as st  # noqa: E402

from app import paginas  # noqa: E402
from app.estilos import aplicar_estilos, marca_lateral  # noqa: E402

st.set_page_config(page_title="Proyecto Red · ADA 2026-2", layout="wide")
aplicar_estilos()
marca_lateral()

# El orden debe coincidir con ICONOS_NAV de app/estilos.py
navegacion = st.navigation([
    st.Page(paginas.cargar_caso, title="Cargar caso", default=True),
    st.Page(paginas.evidencias, title="Evidencias", url_path="evidencias"),
    st.Page(paginas.modo_demo, title="Modo demo", url_path="demo"),
    st.Page(paginas.experimentos, title="Experimentos", url_path="experimentos"),
])
navegacion.run()
