"""
Página Experimentos: las gráficas de tiempo medido contra la teoría y de calidad contra el óptimo,
tal como las dejan los scripts de experimentos/ en resultados/.
"""
import os

import streamlit as st

from app.estilos import encabezado, nota
from experimentos.comun import RAIZ


def experimentos():
    encabezado("Experimentos", "Tiempo medido contra la función de eficiencia teórica y calidad contra el óptimo. "
                               "Se generan con los scripts de experimentos/ (parte1, parte2, influencia y variantes).", "grafica")
    p1, p2, p3, p4 = st.tabs(["Parte 1: reparto", "Parte 2: selección", "Parte 2: influencia", "Variante V1: costos"])
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
    with p3:
        nota("Con la utilidad de influencia de los casos de la profesora (python -m experimentos.influencia).")
        _figura("influencia/variaN.png", "Tiempo del voraz al variar N (k = 10)", "Crece como N², por la ganancia en O(N).")
        _figura("influencia/variak.png", "Tiempo del voraz al variar k (N = 400)", "Crecimiento lineal en k.")
        _figura("influencia/cota.png", "La cota (1 − 1/e) en 300 instancias propias",
                "Sin costos ninguna instancia baja de la cota; con costos algunas sí, porque ahí la garantía no aplica.")
    with p4:
        nota("Algoritmos de la variante V1 (python -m experimentos.variantes).")
        _figura("variantes/calidad.png", "Calidad contra el óptimo",
                "Izquierda: el cupo no restringe y valen las cotas ½(1 − 1/e) de A y 1 − 1/e de B. Derecha: el cupo "
                "restringe; solo valen 1/k y 1/⌈k/3⌉.")
        _figura("variantes/tiempo_A.png", "Tiempo del algoritmo A (k = 10)", "Crece como N²·k, igual que el voraz base.")
        _figura("variantes/tiempo_B.png", "Tiempo del algoritmo B (k = 5)", "Crece como C(N, 3)·N²·k = O(N⁵·k).")


def _figura(ruta, titulo, texto):
    completa = os.path.join(RAIZ, "resultados", ruta)
    st.markdown(f"**{titulo}**")
    nota(texto)
    if os.path.exists(completa):
        st.image(completa, width="stretch")
    else:
        nota(f"No existe resultados/{ruta}: corre el experimento correspondiente.")
    st.write("")
