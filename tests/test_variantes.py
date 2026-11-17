"""
Variante V1 (costos de participación): algoritmos A y B de docs/03_variantes.md.
Uso:  python -m pytest tests/test_variantes.py
"""
import json
import math
import os
from itertools import combinations

import pytest

from ada.casos_red import caso_red_sintetico, leer_caso_red
from ada.generadores import instancia_costos
from ada.parte2.fuerza_bruta import fuerza_bruta_general
from ada.parte2.influencia import f_influencia, matriz_influencia, voraz_influencia
from ada.solucion_red import resolver_caso_red
from ada.variantes.costos import algoritmo_a, algoritmo_b, k_max

CASO_PROFESORA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "casos", "profesora", "entrada_G2_red_15_nodos.json")

COTA_A = (1 - 1 / math.e) / 2          # Teorema V1.1
COTA_B = 1 - 1 / math.e                # Teorema V1.2


def _optimo(inst):
    return fuerza_bruta_general(lambda S: f_influencia(list(S), inst.a, inst.W), inst.k,
                                range(inst.N), inst.costos, inst.P)[1]


def _factible(S, costos, P, k):
    return len(S) <= k and len(set(S)) == len(S) and sum(costos[i] for i in S) <= P


def test_contraejemplo_del_voraz_por_ganancia():
    """Instancia 1 (sección V1.4): el voraz por ganancia obtiene 10; la razón y A, 45."""
    a, c, W = [10] + [9] * 5, [10] + [2] * 5, matriz_influencia(6, [])
    assert voraz_influencia(a, W, 5, costos=c, presupuesto=10)[1] == 10
    assert voraz_influencia(a, W, 5, costos=c, presupuesto=10, razon=True)[1] == 45
    assert algoritmo_a(a, W, 5, c, 10)[1] == 45


@pytest.mark.parametrize("P", [10, 100, 1000])
def test_contraejemplo_del_voraz_por_razon(P):
    """Instancia 2: el voraz por razón obtiene 2 (razón 2/P -> 0); A y B obtienen P."""
    a, c, W = [2, P], [1, P], matriz_influencia(2, [])
    assert voraz_influencia(a, W, 2, costos=c, presupuesto=P, razon=True)[1] == 2
    assert algoritmo_a(a, W, 2, c, P)[1] == P
    assert algoritmo_b(a, W, 2, c, P)[1] == P


@pytest.mark.parametrize("k", [3, 4, 6])
def test_ejemplo_donde_a_llega_justo_a_1_sobre_k(k):
    """Sección V1.7: k baratos (c = 1, f = 1) y k caros (c = P/k, f = P/2k) con P = 2k²."""
    P = 2 * k * k
    a, c = [1] * k + [P / (2 * k)] * k, [1] * k + [P // k] * k
    W = matriz_influencia(2 * k, [])
    _, opt = fuerza_bruta_general(lambda S: f_influencia(list(S), a, W), k, range(2 * k), c, P)
    assert opt == k * k
    assert algoritmo_a(a, W, k, c, P)[1] == pytest.approx(opt / k)
    assert algoritmo_b(a, W, k, c, P)[1] >= opt / math.ceil(k / 3) - 1e-9


def test_cotas_cuando_el_cupo_no_restringe():
    """Teoremas V1.1 y V1.2 en 150 instancias con k = N (solo presupuesto)."""
    for s in range(150):
        inst = instancia_costos(6 + s % 5, semilla=s, regimen="presupuesto")
        opt = _optimo(inst)
        SA, vA = algoritmo_a(inst.a, inst.W, inst.k, inst.costos, inst.P)
        SB, vB = algoritmo_b(inst.a, inst.W, inst.k, inst.costos, inst.P)
        assert _factible(SA, inst.costos, inst.P, inst.k) and _factible(SB, inst.costos, inst.P, inst.k)
        assert vA == pytest.approx(f_influencia(SA, inst.a, inst.W))
        assert vB == pytest.approx(f_influencia(SB, inst.a, inst.W))
        assert vA >= COTA_A * opt - 1e-9
        assert vB >= COTA_B * opt - 1e-9


def test_cotas_cuando_el_cupo_restringe():
    """Teorema V1.4 en 150 instancias con k < k_max(P): A >= OPT/k y B >= OPT/⌈k/3⌉."""
    for s in range(150):
        inst = instancia_costos(7 + s % 5, semilla=s, regimen="mixto")
        assert inst.k < k_max(inst.costos, inst.P)
        opt = _optimo(inst)
        SA, vA = algoritmo_a(inst.a, inst.W, inst.k, inst.costos, inst.P)
        SB, vB = algoritmo_b(inst.a, inst.W, inst.k, inst.costos, inst.P)
        assert _factible(SA, inst.costos, inst.P, inst.k) and _factible(SB, inst.costos, inst.P, inst.k)
        assert vA >= opt / inst.k - 1e-9
        assert vB >= opt / math.ceil(inst.k / 3) - 1e-9
        if inst.k <= 3:                      # B revisa todos los grupos factibles: es exacto
            assert vB == pytest.approx(opt)


def test_k_max_coincide_con_la_definicion():
    for s in range(40):
        inst = instancia_costos(8, semilla=s)
        mayor = max(len(S) for j in range(9) for S in combinations(range(8), j)
                    if sum(inst.costos[i] for i in S) <= inst.P)
        assert k_max(inst.costos, inst.P) == mayor


def test_nodos_con_costo_cero_y_nodos_que_no_caben():
    """Costo 0: razón infinita, entra primero. Costo > P: se descarta. Nada se rompe."""
    a, W = [5, 1, 8, 3], matriz_influencia(4, [(0, 1, 0.5)])
    c, P = [0, 0, 50, 3], 10                  # el nodo 2 no cabe ni solo
    for alg in (algoritmo_a, algoritmo_b):
        S, v = alg(a, W, 4, c, P)
        assert 2 not in S and {0, 1} <= set(S)
        assert _factible(S, c, P, 4)
    assert algoritmo_a(a, W, 4, [50] * 4, P) == ([], 0.0)   # ningún nodo cabe


def test_razon_sin_costos_es_un_error():
    a, W = [1, 2], matriz_influencia(2, [])
    with pytest.raises(ValueError):
        voraz_influencia(a, W, 1, razon=True)


@pytest.mark.parametrize("seleccion", ["A", "B"])
def test_caso_de_la_profesora_con_los_algoritmos_de_v1(seleccion):
    """Las T rondas con A o B cumplen todas las restricciones y quedan cerca del óptimo de cada ronda."""
    with open(CASO_PROFESORA, encoding="utf-8") as fh:
        caso = leer_caso_red(json.load(fh))
    res = resolver_caso_red(caso, seleccion=seleccion)
    assert res["cumple_todo"]
    for r in res["rondas"]:
        assert r["utilidad_conjunta"] >= r["optimo"]["valor"] / math.ceil(caso.k / 3) - 1e-9   # Teorema V1.4
        assert [p["nodo"] for p in r["traza_seleccion"]] == r["seleccion"]


def test_algoritmo_b_rechaza_casos_grandes():
    caso = leer_caso_red(caso_red_sintetico("grande", N=60, T=1, k=5, B=10, P=20))
    with pytest.raises(ValueError):
        resolver_caso_red(caso, seleccion="B")
