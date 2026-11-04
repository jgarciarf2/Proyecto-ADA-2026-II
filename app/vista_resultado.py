"""
Vista completa del resultado de un caso: métricas, pestañas con gráficas y trazas,
y la verificación de restricciones.
"""
import json
import math

import pandas as pd
import streamlit as st

from ada.casos import leer_caso, utilidad_a_dict
from app import graficas
from app.estilos import AZUL, ROJO, VERDE, chips_verificacion, metricas, nota
from app.vista_red import mostrar_red

COTA = 1 - 1 / math.e


def _f(v, d=3):
    return f"{v:,.{d}f}".replace(",", " ")


def mostrar(entrada, res, clave):
    """entrada = caso en JSON (dict); res = resultado serializado; clave = prefijo único para widgets."""
    if res.get("formato") == "red":          # caso con el formato de la profesora
        return mostrar_red(entrada, res, clave)
    caso = leer_caso(entrada)
    t = res["tiempo_s"]
    n_ok = sum(v["cumple"] for v in res["verificaciones"])
    n_total = len(res["verificaciones"])

    st.markdown(f"#### {res['caso']}")
    nota(f"N = {res['N']} nodos · k = {res['k']} · B = {res['B']} · M = {res['M']} tipos de datos")

    # cada subtítulo son dos líneas cortas, para que no se partan en cualquier punto
    if res["optimo"]:
        opt = res["optimo"]["valor"]
        sub_f = (f"óptimo {_f(opt, 2)} · razón {res['utilidad_conjunta'] / opt:.3f}"
                 f"<br>garantía (1−1/e): ≥ {_f(COTA * opt, 2)}")
    else:
        sub_f = f"óptimo no calculado (C(N,k) grande)<br>el óptimo no pasa de {_f(res['utilidad_conjunta'] / COTA, 2)}"
    metricas([
        ("objetivo", "Utilidad conjunta f(S)", _f(res["utilidad_conjunta"]), sub_f, AZUL),
        ("capas", "Utilidad del reparto U(x)", _f(res["utilidad_reparto"]),
         f"B = {res['B']} entre {len(res['seleccion'])} nodos<br>reparto óptimo (voraz exacto)", AZUL),
        ("reloj", "Tiempo de la solución", f"{_f(t['total'] * 1e3, 3)} ms",
         f"selección {_f(t['seleccion'] * 1e3, 3)} ms<br>reparto {_f(t['reparto'] * 1e3, 3)} ms", "#0f172a"),
        ("escudo", "Restricciones", f"{n_ok} / {n_total}",
         ("todas se cumplen" if res["cumple_todo"] else "hay restricciones que NO se cumplen")
         + "<br>detalle al final de la página", VERDE if res["cumple_todo"] else ROJO),
    ])

    tab_sel, tab_rep, tab_traza, tab_datos = st.tabs(["Selección", "Reparto", "Traza", "Datos del caso"])

    with tab_sel:
        izq, der = st.columns([1.15, 1], gap="large")
        with izq:
            st.markdown("**¿Cómo eligió el voraz?**")
            guias = ("Verde: el óptimo. Roja: la garantía (1−1/e)·óptimo." if res["optimo"]
                     else "Roja: techo del óptimo, f(S)/(1−1/e).")
            nota("Barras: lo que aportó cada nodo al entrar; bajan paso a paso porque la utilidad es "
                 f"submodular. Naranja: utilidad acumulada. {guias}")
            st.plotly_chart(graficas.seleccion(res), width="stretch", key=f"{clave}-sel")
        with der:
            fig, cubiertos, repetidos = graficas.cobertura(caso, res)
            st.markdown("**¿Qué cubre cada nodo elegido?**")
            nota(f"Solo se muestran los {cubiertos} tipos cubiertos. Azul: lo cubre un solo nodo. "
                 f"Naranja: lo cubren dos o más ({repetidos} tipos), así que ese aporte se repite.")
            st.plotly_chart(fig, width="stretch", key=f"{clave}-cob")

    with tab_rep:
        fig, nivel, siguiente = graficas.reparto(caso, res)
        st.markdown("**El presupuesto como nivel de agua**")
        detalle = ""
        if nivel is not None and siguiente is not None:
            detalle = (f" La unidad entregada más baja vale {nivel:.4f} y la mejor que quedó sin entregar "
                       f"vale {siguiente:.4f}, así que mover una unidad de un nodo a otro no mejora el total.")
        nota("Cada barra es una unidad de presupuesto para ese nodo y su altura es su ganancia marginal. "
             "Todas las unidades entregadas (azul) quedan por encima del nivel y las demás (gris) por debajo." + detalle)
        st.plotly_chart(fig, width="stretch", key=f"{clave}-rep")
        tabla = pd.DataFrame(res["reparto"]).rename(columns={
            "nodo": "Nodo", "unidades": "Unidades", "utilidad": "Utilidad uᵢ(xᵢ)", "ultima_ganancia": "Última ganancia"})
        st.dataframe(tabla, hide_index=True, width="stretch")

    with tab_traza:
        st.markdown("**Traza de la selección (Parte 2)**")
        st.dataframe(pd.DataFrame(res["traza_seleccion"]).rename(columns={
            "paso": "Paso", "nodo": "Nodo elegido", "ganancia_marginal": "Ganancia marginal",
            "utilidad_acumulada": "Utilidad acumulada", "candidatos_evaluados": "Candidatos evaluados"}),
            hide_index=True, width="stretch")
        st.markdown("**Traza del reparto (Parte 1)**")
        if res["traza_reparto"]:
            st.dataframe(pd.DataFrame(res["traza_reparto"]).rename(columns={
                "unidad": "Unidad", "nodo": "Nodo", "ganancia_marginal": "Ganancia marginal"}),
                hide_index=True, width="stretch", height=280)
        else:
            nota(f"B = {res['B']} es grande: la traza por unidad no se guarda; queda el resumen por nodo "
                 "en la pestaña Reparto.")
        c1, c2, _ = st.columns([1, 1, 2])
        c1.download_button("Descargar resultado.json", json.dumps({"entrada": entrada, "resultado": res},
                           ensure_ascii=False, indent=1), file_name=f"{res['caso']}_resultado.json",
                           mime="application/json", key=f"{clave}-dj", width="stretch")
        c2.download_button("Descargar traza.csv", pd.DataFrame(res["traza_seleccion"]).to_csv(index=False),
                           file_name=f"{res['caso']}_traza_seleccion.csv", mime="text/csv",
                           key=f"{clave}-dc", width="stretch")

    with tab_datos:
        nodos = pd.DataFrame([{
            "Nodo": i, "Elegido": "sí" if str(i) in {str(s) for s in res["seleccion"]} else "",
            "Tipos que cubre": len(c), "Utilidad": _describir(u)}
            for i, c, u in zip(caso.ids, caso.conjuntos, caso.utilidades)])
        st.dataframe(nodos, hide_index=True, width="stretch", height=min(420, 38 + 35 * len(nodos)))
        nota(f"{caso.M} tipos de datos con pesos entre {min(caso.pesos):.2f} y {max(caso.pesos):.2f}.")

    st.write("")
    st.markdown("**Verificación de restricciones**")
    nota("Pasa el mouse sobre cada etiqueta para ver el detalle.")
    chips_verificacion(res["verificaciones"])


def _describir(u):
    d = utilidad_a_dict(u)
    if d["familia"] == "tabla":
        return f"tabla de {len(d['valores'])} valores"
    nombres = {"log": "a·ln(1+x)", "sqrt": "a·√x", "exp": "a·(1−e^(−b·x))"}
    params = ", ".join(f"{k} = {v:.2f}" for k, v in d.items() if k != "familia")
    return f"{nombres[d['familia']]}  ({params})"
