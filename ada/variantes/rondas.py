"""V2: resolver las rondas con fallas temporales y reproducibles.

El generador de fallas cuesta O(N) por ronda y usa O(N) memoria transitoria.
La resolución total reutiliza la selección y el reparto de ``ada.solucion_red``;
con influencia densa cuesta O(T * (N² k + B log(k + 1))).
"""
import random
import time

from ada.solucion_red import _ronda
from ada.verificacion import _registro, todas_cumplen


def generar_fallas(N, T, probabilidad, semilla):
    """Produce disponibilidad/caídas por ronda; las fallas son Bernoulli iid.

    La disponibilidad se conoce antes de resolver la ronda. Un nodo caído vuelve
    a ser candidato en rondas posteriores. Costo O(TN), espacio adicional O(N).
    """
    if not 0 <= probabilidad <= 1:
        raise ValueError("probabilidad debe estar entre 0 y 1")
    if not isinstance(semilla, int):
        raise ValueError("semilla debe ser un entero")
    rng = random.Random(semilla)
    for _ in range(T):
        caidos = {i for i in range(N) if rng.random() < probabilidad}
        yield {"disponibles": set(range(N)) - caidos, "caidos": caidos}


def resolver_caso_red_v2(caso, probabilidad_falla, semilla_fallas=0, con_optimo=True):
    """Resuelve un caso con fallas temporales conocidas al inicio de cada ronda.

    Cada ronda reutiliza el voraz por ganancia con las restricciones k y P, y
    luego el reparto óptimo de ruido con topes por nodo. El tiempo total medido
    incluye generar fallas, seleccionar y repartir en cada ronda, igual que el
    cronómetro base excluye la serialización y la escritura de archivos.
    """
    if not 0 <= probabilidad_falla <= 1:
        raise ValueError("probabilidad_falla debe estar entre 0 y 1")
    if not isinstance(semilla_fallas, int):
        raise ValueError("semilla_fallas debe ser un entero")

    usado = [0] * caso.N
    rondas = []
    fallas_por_ronda = iter(generar_fallas(caso.N, caso.T, probabilidad_falla, semilla_fallas))
    for t in range(1, caso.T + 1):
        t0 = time.perf_counter()
        fallas = next(fallas_por_ronda)
        t_fallas = time.perf_counter() - t0
        disponibles = fallas["disponibles"]
        caidos = fallas["caidos"]
        res = _ronda(caso, t, usado, con_optimo, disponibles=disponibles)
        res["disponibles"] = [caso.ids[i] for i in sorted(disponibles)]
        res["caidos"] = [caso.ids[i] for i in sorted(caidos)]
        seleccionados = set(res["seleccion"])
        caidos_ids = {caso.ids[i] for i in caidos}
        sin_caidos = not (seleccionados & caidos_ids)
        res["verificaciones"].append(_registro(
            f"ronda {t}: nodos caidos no seleccionados", sin_caidos,
            "ningún nodo caído fue seleccionado" if sin_caidos else "se seleccionó un nodo caído"))
        res["cumple_todo"] = todas_cumplen(res["verificaciones"])
        res["tiempo_s"]["fallas"] = max(0.0, t_fallas)
        res["tiempo_s"]["total"] += res["tiempo_s"]["fallas"]
        rondas.append(res)

    global_ok = [_registro(
        "presupuesto total por nodo",
        all(u <= p for u, p in zip(usado, caso.presupuesto_nodo)),
        "ningún nodo supera su presupuesto total")]
    todas = [v for r in rondas for v in r["verificaciones"]] + global_ok
    return {
        "formato": "red", "variante": "V2", "caso": caso.nombre,
        "N": caso.N, "T": caso.T, "k": caso.k, "B": caso.B, "P": caso.P,
        "probabilidad_falla": probabilidad_falla, "semilla_fallas": semilla_fallas,
        "rondas": rondas,
        "utilidad_conjunta_total": sum(r["utilidad_conjunta"] for r in rondas),
        "utilidad_reparto_total": sum(r["utilidad_reparto"] for r in rondas),
        "presupuesto_usado": [
            {"nodo": caso.ids[i], "usado": usado[i], "tope": caso.presupuesto_nodo[i]}
            for i in range(caso.N)],
        "verificacion_global": global_ok, "cumple_todo": todas_cumplen(todas),
        "tiempo_s": {"total": sum(r["tiempo_s"]["total"] for r in rondas)},
        "supuestos": [
            "fallas Bernoulli independientes entre nodos y rondas, con probabilidad común p",
            "fallas temporales conocidas al inicio de la ronda; el nodo vuelve en la siguiente",
            "una falla no consume el presupuesto acumulado de ruido del nodo",
            "uᵢ(x) = aᵢ·ln(1 + x) y utilidad de influencia según el modelo base"],
    }
