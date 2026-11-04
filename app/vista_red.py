"""
Vista del resultado de un caso con el formato de la profesora: varias rondas, grafo de
influencia, costos de participación y presupuesto total por nodo.
"""
import json
from types import SimpleNamespace

import pandas as pd
import streamlit as st

from ada.casos_red import leer_caso_red
from ada.utilidades import UtilidadConTope, UtilidadLog
from app import graficas
from app.estilos import AZUL, ROJO, VERDE, aviso, chips_verificacion, metricas, nota


def _f(v, d=3):
    return f"{v:,.{d}f}".replace(",", " ")


def mostrar_red(entrada, res, clave):
    caso = leer_caso_red(entrada, res["caso"])
    rondas = res["rondas"]
    todas = [v for r in rondas for v in r["verificaciones"]] + res["verificacion_global"]
    n_ok = sum(v["cumple"] for v in todas)
    iguales = sum(1 for r in rondas if r["optimo"] and abs(r["utilidad_conjunta"] - r["optimo"]["valor"]) < 1e-9)
    con_opt = sum(1 for r in rondas if r["optimo"])

    st.markdown(f"#### {res['caso']}")
    nota(f"N = {res['N']} nodos · {res['T']} rondas · k = {res['k']} por ronda · B = {res['B']} por ronda · "
         f"presupuesto de participación P = {res['P']} por ronda")
    aviso("<b>Supuestos provisionales</b> (falta confirmarlos con la profesora): " + "; ".join(res["supuestos"]) + ".")

    metricas([
        ("objetivo", f"Utilidad conjunta ({res['T']} rondas)", _f(res["utilidad_conjunta_total"]),
         f"igual al óptimo en {iguales} de {con_opt} rondas<br>óptimo por fuerza bruta en cada ronda", AZUL),
        ("capas", f"Utilidad del reparto ({res['T']} rondas)", _f(res["utilidad_reparto_total"]),
         f"B = {res['B']} por ronda<br>reparto óptimo (voraz exacto)", AZUL),
        ("reloj", "Tiempo de la solución", f"{_f(res['tiempo_s']['total'] * 1e3)} ms",
         f"{res['T']} rondas<br>selección + reparto + verificación", "#0f172a"),
        ("escudo", "Restricciones", f"{n_ok} / {len(todas)}",
         ("todas se cumplen" if res["cumple_todo"] else "hay restricciones que NO se cumplen")
         + "<br>detalle al final de la página", VERDE if res["cumple_todo"] else ROJO),
    ])

    st.markdown("**Resumen por ronda**")
    st.dataframe(pd.DataFrame([{
        "Ronda": r["ronda"], "Participantes": ", ".join(map(str, r["seleccion"])),
        "Costo (≤ P)": f"{r['costo_participacion']} / {res['P']}",
        "f(S)": round(r["utilidad_conjunta"], 3),
        "Óptimo f(S)": round(r["optimo"]["valor"], 3) if r["optimo"] else "—",
        "U(x)": round(r["utilidad_reparto"], 3),
        "Presupuesto repartido": f"{sum(f['unidades'] for f in r['reparto'])} / {res['B']}",
        "Tiempo (ms)": round(r["tiempo_s"]["total"] * 1e3, 3)} for r in rondas]),
        hide_index=True, width="stretch")

    st.markdown("**Presupuesto de ruido usado por nodo**")
    nota("Cada color es una ronda. Ningún nodo puede pasar su presupuesto total (línea roja): cuando a un nodo "
         "le queda poco, el reparto de la ronda le da como mucho lo que le queda.")
    st.plotly_chart(graficas.presupuesto_por_nodo(res["presupuesto_usado"], rondas), width="stretch",
                    key=f"{clave}-uso")

    st.divider()
    t = st.segmented_control("Ver el detalle de la ronda", [r["ronda"] for r in rondas],
                             format_func=lambda x: f"Ronda {x}", default=1, key=f"{clave}-ronda") or 1
    r = rondas[t - 1]
    tab_sel, tab_rep, tab_traza, tab_datos = st.tabs(["Selección", "Reparto", "Traza", "Datos del caso"])

    with tab_sel:
        izq, der = st.columns([1, 1.15], gap="large")
        with izq:
            st.markdown("**¿Cómo eligió el voraz?**")
            nota("Barras: lo que aportó cada nodo al entrar. Naranja: utilidad acumulada. Verde: el óptimo de la "
                 f"ronda. Con el límite de costo P = {res['P']} la cota (1 − 1/e) no está garantizada (variante V1), "
                 "por eso no se dibuja.")
            st.plotly_chart(graficas.seleccion(r, con_garantia=False), width="stretch", key=f"{clave}-sel")
        with der:
            st.markdown("**¿A quién influye cada participante?**")
            nota("Color = peso de influencia del participante sobre cada nodo. La última fila es la probabilidad "
                 "de que el nodo quede influido por algún participante; f(S) suma esas probabilidades por aᵥ.")
            st.plotly_chart(graficas.influencia(caso.ids, caso.W, r["seleccion"]), width="stretch",
                            key=f"{clave}-inf")

    with tab_rep:
        pos = {str(i): n for n, i in enumerate(caso.ids)}
        restante = {str(f["nodo"]): f["restante_antes"] for f in r["reparto"]}
        utilidades = [UtilidadConTope(UtilidadLog(caso.a[n]), restante.get(str(i), caso.presupuesto_nodo[n]))
                      for n, i in enumerate(caso.ids)]
        fig, nivel, siguiente = graficas.reparto(SimpleNamespace(ids=caso.ids, utilidades=utilidades), r)
        st.markdown("**El presupuesto de la ronda como nivel de agua**")
        detalle = ""
        if nivel is not None and siguiente is not None:
            detalle = (f" La unidad entregada más baja vale {nivel:.4f} y la mejor que quedó sin entregar "
                       f"vale {siguiente:.4f}.")
        nota("Cada barra es una unidad para ese nodo, con uᵢ(x) = aᵢ·ln(1+x). Si al nodo se le acaba su presupuesto "
             "total, sus siguientes unidades valen 0 y no aparecen." + detalle)
        st.plotly_chart(fig, width="stretch", key=f"{clave}-rep")
        st.dataframe(pd.DataFrame(r["reparto"]).rename(columns={
            "nodo": "Nodo", "unidades": "Unidades", "utilidad": "Utilidad uᵢ(xᵢ)",
            "ultima_ganancia": "Última ganancia", "restante_antes": "Le quedaban"}), hide_index=True, width="stretch")

    with tab_traza:
        st.markdown(f"**Traza de la selección, ronda {t}**")
        st.dataframe(pd.DataFrame(r["traza_seleccion"]).rename(columns={
            "paso": "Paso", "nodo": "Nodo elegido", "ganancia_marginal": "Ganancia marginal",
            "utilidad_acumulada": "Utilidad acumulada", "candidatos_evaluados": "Candidatos evaluados",
            "costo_acumulado": "Costo acumulado"}), hide_index=True, width="stretch")
        st.markdown(f"**Traza del reparto, ronda {t}**")
        st.dataframe(pd.DataFrame(r["traza_reparto"]).rename(columns={
            "unidad": "Unidad", "nodo": "Nodo", "ganancia_marginal": "Ganancia marginal"}),
            hide_index=True, width="stretch", height=280)
        st.download_button("Descargar resultado.json", json.dumps({"entrada": entrada, "resultado": res},
                           ensure_ascii=False, indent=1), file_name=f"{res['caso']}_resultado.json",
                           mime="application/json", key=f"{clave}-dj")

    with tab_datos:
        uso = {str(p["nodo"]): p["usado"] for p in res["presupuesto_usado"]}
        st.dataframe(pd.DataFrame([{
            "Nodo": i, "Coeficiente aᵢ": caso.a[n], "Costo cᵢ": caso.costos[n],
            "Presupuesto total": caso.presupuesto_nodo[n], "Usado en total": uso[str(i)],
            "Rondas en que participó": sum(1 for x in rondas if str(i) in map(str, x["seleccion"]))}
            for n, i in enumerate(caso.ids)]), hide_index=True, width="stretch")
        nota(f"Grafo de influencia con {sum(1 for u in range(caso.N) for v in range(u + 1, caso.N) if caso.W[u][v] > 0)} "
             "aristas (no dirigido).")

    st.write("")
    st.markdown(f"**Verificación de restricciones, ronda {t}**")
    nota("Pasa el mouse sobre cada etiqueta para ver el detalle.")
    chips_verificacion([{**v, "restriccion": v["restriccion"].split(": ", 1)[1]} for v in r["verificaciones"]])
    st.write("")
    st.markdown("**Verificación de todas las rondas juntas**")
    chips_verificacion(res["verificacion_global"])
