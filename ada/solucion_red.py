"""
Solución base para un caso de la profesora: T rondas; en cada una se eligen los
participantes (Parte 2, utilidad de influencia) y se reparte el presupuesto de ruido
entre ellos (Parte 1), sin pasar el presupuesto total de cada nodo.

Por ronda, con N nodos, cupo k y presupuesto B:
    selección  O(N · k · N)          voraz de influencia (cada ganancia cuesta O(N))
    reparto    O(k + B log k)        voraz con montículo sobre los elegidos
    verificar  O(N · k)              recalcular f(S) y U(x)
    T_total = O(T · (N²·k + B log k))
"""
import time

from ada.parte1.voraz import voraz_heap
from ada.parte2.fuerza_bruta import fuerza_bruta_general, subconjuntos_a_probar
from ada.parte2.influencia import f_influencia, voraz_influencia
from ada.utilidades import UtilidadConTope, UtilidadLog
from ada.verificacion import (_registro, todas_cumplen, verificar_reparto, verificar_seleccion,
                              verificar_valor)

LIMITE_FUERZA_BRUTA = 200_000      # subconjuntos máximos para calcular el óptimo de una ronda


def resolver_caso_red(caso, con_optimo=True):
    """Devuelve un diccionario serializable con el resultado de cada ronda y los totales."""
    usado = [0] * caso.N
    rondas = []
    for t in range(1, caso.T + 1):
        rondas.append(_ronda(caso, t, usado, con_optimo))
    global_ok = [_registro("presupuesto total por nodo",
                           all(u <= p for u, p in zip(usado, caso.presupuesto_nodo)),
                           f"máximo usado = {max(usado)}, tope = {min(caso.presupuesto_nodo)}")]
    verificaciones = [v for r in rondas for v in r["verificaciones"]] + global_ok
    return {
        "formato": "red", "caso": caso.nombre,
        "N": caso.N, "T": caso.T, "k": caso.k, "B": caso.B, "P": caso.P,
        "rondas": rondas,
        "utilidad_conjunta_total": sum(r["utilidad_conjunta"] for r in rondas),
        "utilidad_reparto_total": sum(r["utilidad_reparto"] for r in rondas),
        "presupuesto_usado": [{"nodo": caso.ids[i], "usado": usado[i], "tope": caso.presupuesto_nodo[i]}
                              for i in range(caso.N)],
        "verificacion_global": global_ok,
        "cumple_todo": todas_cumplen(verificaciones),
        "tiempo_s": {"total": sum(r["tiempo_s"]["total"] for r in rondas)},
        "supuestos": ["uᵢ(x) = aᵢ·ln(1 + x) en cada ronda",
                      "f(S) = Σᵥ aᵥ·(1 − Πᵤ∈S (1 − wᵤᵥ)), con wᵥᵥ = 1",
                      "grafo no dirigido; se exige |S| ≤ k y Σ cᵢ ≤ P a la vez",
                      "solo participan nodos con presupuesto restante > 0"],
    }


def _ronda(caso, t, usado, con_optimo):
    ids = caso.ids
    restante = [p - u for p, u in zip(caso.presupuesto_nodo, usado)]
    candidatos = [i for i in range(caso.N) if restante[i] > 0]

    traza_sel = []
    t0 = time.perf_counter()
    S, valor_f = voraz_influencia(caso.a, caso.W, caso.k, candidatos=candidatos,
                                  costos=caso.costos, presupuesto=caso.P, traza=traza_sel)
    t_sel = time.perf_counter() - t0

    utilidades = [UtilidadConTope(UtilidadLog(caso.a[i]), restante[i]) for i in S]
    traza_local = []
    t0 = time.perf_counter()
    x, valor_U = voraz_heap(utilidades, caso.B, traza=traza_local)
    t_rep = time.perf_counter() - t0
    for i, xi in zip(S, x):
        usado[i] += xi

    costo = sum(caso.costos[i] for i in S)
    verificaciones = (
        verificar_seleccion(S, caso.N, caso.k)
        + [_registro("costo de participacion <= P", costo <= caso.P, f"costo = {costo}, P = {caso.P}")]
        + verificar_reparto(x, caso.B)
        + [_registro("x_i <= presupuesto restante", all(xi <= restante[i] for i, xi in zip(S, x)),
                     "ningún nodo pasa su presupuesto restante")]
        + verificar_valor("f(S)", valor_f, f_influencia(S, caso.a, caso.W))
        + verificar_valor("U(x)", valor_U, sum(u(xi) for u, xi in zip(utilidades, x)))
    )
    for v in verificaciones:
        v["restriccion"] = f"ronda {t}: {v['restriccion']}"

    optimo = None
    if con_optimo and subconjuntos_a_probar(len(candidatos), caso.k) <= LIMITE_FUERZA_BRUTA:
        S_opt, v_opt = fuerza_bruta_general(lambda A: f_influencia(A, caso.a, caso.W), caso.k, candidatos,
                                            costos=caso.costos, presupuesto=caso.P)
        optimo = {"valor": v_opt, "seleccion": [ids[i] for i in S_opt], "metodo": "fuerza bruta"}

    ultima = {}
    for r in traza_local:
        ultima[S[r["nodo"]]] = r["ganancia_marginal"]
    return {
        "ronda": t,
        "candidatos": [ids[i] for i in candidatos],
        "seleccion": [ids[i] for i in S],
        "costo_participacion": costo,
        "utilidad_conjunta": valor_f,
        "optimo": optimo,
        "reparto": [{"nodo": ids[i], "unidades": xi, "utilidad": u(xi), "ultima_ganancia": ultima.get(i),
                     "restante_antes": restante[i]} for i, xi, u in zip(S, x, utilidades)],
        "utilidad_reparto": valor_U,
        "verificaciones": verificaciones,
        "cumple_todo": todas_cumplen(verificaciones),
        "tiempo_s": {"seleccion": t_sel, "reparto": t_rep, "total": t_sel + t_rep},
        "traza_seleccion": [{**p, "nodo": ids[p["nodo"]]} for p in traza_sel],
        "traza_reparto": [{**p, "nodo": ids[S[p["nodo"]]]} for p in traza_local],
    }
