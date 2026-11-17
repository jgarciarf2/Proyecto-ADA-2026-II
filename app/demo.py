"""
Modo demo: casos sintéticos con el modelo de la profesora (grafo de influencia, T rondas,
cupo k y presupuesto de participación P), para explicar en vivo la solución y la variante V1.
"""
import json
from math import comb

import pandas as pd
import streamlit as st

from ada.casos_red import caso_red_sintetico, leer_caso_red
from ada.variantes.costos import k_max
from app.estilos import aviso, encabezado, nota
from app.paginas import SELECCION_UI, _resolver
from app.vista_resultado import mostrar

LIMITE_B_DEMO = 5_000        # grupos de 3 nodos: con N ≤ 32 el algoritmo B responde en pocos segundos


def modo_demo():
    encabezado("Modo demo", "Casos sintéticos con el modelo de la profesora: mueve los controles y compara los "
                            "algoritmos de selección en vivo.", "controles")
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        N = st.slider("Nodos (N)", 6, 30, 12)
        T = st.slider("Rondas (T)", 1, 4, 2)
        densidad = st.slider("Densidad del grafo", 0.0, 1.0, 0.6, step=0.1)
    with c2:
        k = st.slider("Cupo por ronda (k)", 1, N - 1, min(4, N - 1))
        P = st.slider("Presupuesto de participación (P)", 1, 60, 14)
        B = st.slider("Presupuesto de ruido (B)", 0, 60, 20)
    with c3:
        semilla = st.number_input("Semilla", 0, 10_000, 7, step=1)
        etiqueta = st.selectbox("Algoritmo que se muestra abajo", list(SELECCION_UI))

    datos = caso_red_sintetico(f"demo_N{N}_T{T}_k{k}_P{P}", N, T, k, B, P, R=max(1, B), densidad=densidad,
                               semilla=int(semilla))
    texto = json.dumps(datos, sort_keys=True)
    caso = leer_caso_red(datos, datos["nombre"])
    tope = k_max(caso.costos, P)
    regimen = ("el cupo no restringe (k ≥ kₘₐₓ): valen las cotas ½(1 − 1/e) del algoritmo A y 1 − 1/e del B"
               if k >= tope else
               "el cupo restringe (k < kₘₐₓ): solo valen las cotas 1/k del algoritmo A y 1/⌈k/3⌉ del B")
    aviso(f"Con estos costos caben como máximo kₘₐₓ(P) = {tope} nodos en P = {P}, y k = {k}: {regimen}.")

    filas, resultados = [], {}
    for nombre, clave in SELECCION_UI.items():
        if clave == "B" and comb(N, 3) > LIMITE_B_DEMO:
            filas.append({"Algoritmo": nombre, "f(S) total": "—", "Óptimo total": "—", "f / óptimo": "—",
                          "Tiempo (ms)": f"no se calcula: C({N}, 3) > {LIMITE_B_DEMO}"})
            continue
        _, res = _resolver(texto, True, clave)
        resultados[clave] = res
        optimos = [r["optimo"]["valor"] for r in res["rondas"] if r["optimo"]]
        opt = sum(optimos) if len(optimos) == len(res["rondas"]) else None
        filas.append({"Algoritmo": nombre, "f(S) total": round(res["utilidad_conjunta_total"], 3),
                      "Óptimo total": round(opt, 3) if opt is not None else "—",
                      "f / óptimo": round(res["utilidad_conjunta_total"] / opt, 3) if opt else "—",
                      "Tiempo (ms)": round(sum(r["tiempo_s"]["seleccion"] for r in res["rondas"]) * 1e3, 2)})
    st.markdown("**Comparación de los algoritmos de selección**")
    nota("Tiempo: solo la selección, sumando las rondas. El óptimo se calcula por fuerza bruta en cada ronda.")
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")

    clave = SELECCION_UI[etiqueta]
    st.divider()
    if clave in resultados:
        mostrar(datos, resultados[clave], clave="demo")
    else:
        aviso("El algoritmo B no se calcula con tantos nodos en el modo demo. Baja N o elige otro algoritmo.")
