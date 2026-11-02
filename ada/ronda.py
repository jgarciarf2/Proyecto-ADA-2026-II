"""
Solución base de una ronda: primero se eligen los participantes (Parte 2) y
luego se reparte el presupuesto entre ellos (Parte 1).

Costo total, con N candidatos, cupo k, |D_i| = d y presupuesto B:
    selección  O(N · k · d)       (voraz submodular)
    reparto    O(k + B log k)     (voraz con heap sobre los k elegidos)
    verificar  O(k · d)
    T = O(N·k·d + B log k)
"""
import time

from ada.parte1.voraz import voraz_heap
from ada.parte2.cobertura import f
from ada.parte2.voraz import voraz_submodular
from ada.verificacion import todas_cumplen, verificar_reparto, verificar_seleccion, verificar_valor


def resolver_ronda(conjuntos, pesos, k, utilidades, B):
    """
    conjuntos[i], pesos -> utilidad conjunta de cobertura de los N candidatos.
    utilidades[i]       -> utilidad cóncava del nodo i para el reparto.
    Devuelve un diccionario con la selección, el reparto, las verificaciones,
    las trazas de los dos voraces (con los ids originales de los nodos) y los tiempos.
    """
    N = len(conjuntos)

    traza_seleccion = []
    t0 = time.perf_counter()
    S, valor_f = voraz_submodular(conjuntos, pesos, k, traza=traza_seleccion)
    t_seleccion = time.perf_counter() - t0

    traza_local = []
    t0 = time.perf_counter()
    x_local, valor_U = voraz_heap([utilidades[i] for i in S], B, traza=traza_local)
    t_reparto = time.perf_counter() - t0

    # el voraz del reparto numera los elegidos 0..k-1: se traducen a los ids originales
    traza_reparto = [{**r, "nodo": S[r["nodo"]]} for r in traza_local]
    reparto = {nodo: x for nodo, x in zip(S, x_local)}

    verificaciones = (
        verificar_seleccion(S, N, k)
        + verificar_reparto(x_local, B)
        + verificar_valor("f(S)", valor_f, f(S, conjuntos, pesos))
        + verificar_valor("U(x)", valor_U, sum(utilidades[i](reparto[i]) for i in S))
    )
    return {
        "seleccion": S,
        "utilidad_conjunta": valor_f,
        "reparto": reparto,
        "utilidad_reparto": valor_U,
        "verificaciones": verificaciones,
        "cumple_todo": todas_cumplen(verificaciones),
        "traza_seleccion": traza_seleccion,
        "traza_reparto": traza_reparto,
        "resumen_reparto": resumir_reparto(reparto, utilidades, traza_reparto),
        "tiempo_s": {"seleccion": t_seleccion, "reparto": t_reparto, "total": t_seleccion + t_reparto},
    }


def resumir_reparto(reparto, utilidades, traza_reparto):
    """
    Una fila por nodo: unidades recibidas, su utilidad y la ganancia marginal de
    su última unidad. Sirve cuando B es grande y la traza por unidad es muy larga.
    Costo O(k + B).
    """
    ultima = {}
    for r in traza_reparto:
        ultima[r["nodo"]] = r["ganancia_marginal"]
    return [{"nodo": i, "unidades": x, "utilidad": utilidades[i](x), "ultima_ganancia": ultima.get(i)}
            for i, x in reparto.items()]
