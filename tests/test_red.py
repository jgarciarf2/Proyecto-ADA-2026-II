"""
Formato de la profesora: utilidad de influencia, voraz con costos y varias rondas.
Uso:  python -m pytest tests
"""
import json
import math
import os
import random

import pytest

from ada.casos import CasoInvalido
from ada.casos_red import leer_caso_red
from ada.parte2.fuerza_bruta import fuerza_bruta_general
from ada.parte2.influencia import f_influencia, matriz_influencia, voraz_influencia
from ada.solucion_red import resolver_caso_red

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASO_PROFESORA = os.path.join(RAIZ, "casos", "profesora", "entrada_G2_red_15_nodos.json")
COTA = 1 - 1 / math.e


def _grafo_al_azar(N, semilla, densidad=0.5):
    rng = random.Random(semilla)
    a = [rng.uniform(1, 10) for _ in range(N)]
    aristas = [(u, v, round(rng.uniform(0.05, 0.9), 2)) for u in range(N) for v in range(u + 1, N)
               if rng.random() < densidad]
    return a, matriz_influencia(N, aristas)


def test_influencia_es_monotona_y_submodular():
    rng = random.Random(3)
    a, W = _grafo_al_azar(10, semilla=3)
    for _ in range(1500):
        A2 = set(rng.sample(range(10), rng.randint(0, 9)))
        A = {x for x in A2 if rng.random() < 0.5}
        v = rng.choice([x for x in range(10) if x not in A2])
        fA, fA2 = f_influencia(A, a, W), f_influencia(A2, a, W)
        assert fA <= fA2 + 1e-9
        assert f_influencia(A | {v}, a, W) - fA >= f_influencia(A2 | {v}, a, W) - fA2 - 1e-9


def test_traza_del_voraz_coincide_con_f():
    a, W = _grafo_al_azar(12, semilla=4)
    traza = []
    S, valor = voraz_influencia(a, W, 4, traza=traza)
    assert math.isclose(valor, f_influencia(S, a, W))
    assert math.isclose(traza[-1]["utilidad_acumulada"], valor)


def test_voraz_sin_costos_respeta_la_cota():
    for s in range(60):
        a, W = _grafo_al_azar(9, semilla=s, densidad=0.4)
        _, v = voraz_influencia(a, W, 3)
        _, opt = fuerza_bruta_general(lambda A: f_influencia(A, a, W), 3, range(9))
        assert v >= COTA * opt - 1e-9


def test_voraz_con_costos_no_pasa_el_presupuesto():
    rng = random.Random(8)
    for s in range(40):
        a, W = _grafo_al_azar(10, semilla=s)
        costos = [rng.randint(1, 7) for _ in range(10)]
        S, _ = voraz_influencia(a, W, 5, costos=costos, presupuesto=12)
        assert len(S) <= 5 and sum(costos[i] for i in S) <= 12


def test_caso_de_la_profesora_cumple_todo():
    with open(CASO_PROFESORA, encoding="utf-8") as fh:
        datos = json.load(fh)
    caso = leer_caso_red(datos)
    assert caso.N == 15 and caso.T == 3 and caso.k == 5 and caso.B == 30 and caso.P == 24
    res = resolver_caso_red(caso)
    assert res["cumple_todo"], [v for v in res["verificacion_global"] if not v["cumple"]]
    assert len(res["rondas"]) == 3
    for r in res["rondas"]:
        assert len(r["seleccion"]) <= 5 and r["costo_participacion"] <= 24
        assert sum(f["unidades"] for f in r["reparto"]) <= 30
        assert r["utilidad_conjunta"] >= COTA * r["optimo"]["valor"] - 1e-9
    assert all(p["usado"] <= p["tope"] for p in res["presupuesto_usado"])
    json.dumps(res)


@pytest.mark.parametrize("cambio, mensaje", [
    (lambda d: d["parametros"].update(numero_nodos=3), "numero_nodos"),
    (lambda d: d["grafo"].append({"u": "N01", "v": "N99", "peso_influencia": 0.5}), "nodo desconocido"),
    (lambda d: d["grafo"].append({"u": "N01", "v": "N02", "peso_influencia": 1.5}), "entre 0 y 1"),
    (lambda d: d["nodos"][0].update(coeficiente_utilidad=-1), "coeficiente_utilidad"),
])
def test_rechaza_casos_invalidos(cambio, mensaje):
    with open(CASO_PROFESORA, encoding="utf-8") as fh:
        datos = json.load(fh)
    cambio(datos)
    with pytest.raises(CasoInvalido, match=mensaje):
        leer_caso_red(datos)


def test_generador_de_influencia_y_conteo_de_evaluaciones():
    from ada.generadores import instancia_influencia
    inst = instancia_influencia(30, semilla=2, densidad=0.6)
    assert all(inst.W[u][v] == inst.W[v][u] for u in range(30) for v in range(30))
    assert all(inst.W[v][v] == 1.0 for v in range(30))
    _, _, ev = voraz_influencia(inst.a, inst.W, 7, contar=True)
    assert ev == 7 * 30 - 7 * 6 // 2
