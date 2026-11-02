"""
Trazas, verificación de restricciones y solución base de una ronda.  Uso:  python -m pytest tests
"""
import math

from ada.generadores import instancia_cobertura, instancia_reparto
from ada.parte1 import exacto_dp, voraz_heap
from ada.parte2 import voraz_submodular
from ada.ronda import resolver_ronda
from ada.verificacion import todas_cumplen, verificar_reparto, verificar_seleccion


def test_traza_de_seleccion_coincide_con_el_resultado():
    inst = instancia_cobertura(40, 200, 8, semilla=3)
    traza = []
    S, valor = voraz_submodular(inst.conjuntos, inst.pesos, 6, traza=traza)
    assert [r["nodo"] for r in traza] == S
    assert math.isclose(sum(r["ganancia_marginal"] for r in traza), valor)
    assert math.isclose(traza[-1]["utilidad_acumulada"], valor)
    assert [r["candidatos_evaluados"] for r in traza] == [40 - t for t in range(6)]
    # las ganancias marginales no crecen (submodularidad)
    assert all(a["ganancia_marginal"] >= b["ganancia_marginal"] for a, b in zip(traza, traza[1:]))


def test_traza_de_reparto_coincide_con_el_resultado():
    inst = instancia_reparto(10, 60, semilla=4)
    traza = []
    x, total = voraz_heap(inst.utilidades, inst.B, traza=traza)
    assert len(traza) == sum(x) == 60
    assert all(sum(r["nodo"] == i for r in traza) == x[i] for i in range(10))
    assert math.isclose(sum(r["ganancia_marginal"] for r in traza), total)


def test_la_traza_no_cambia_el_resultado():
    inst = instancia_reparto(20, 300, semilla=5)
    assert voraz_heap(inst.utilidades, inst.B, traza=[]) == voraz_heap(inst.utilidades, inst.B)
    cob = instancia_cobertura(30, 100, 5, semilla=5)
    assert voraz_submodular(cob.conjuntos, cob.pesos, 5, traza=[]) == voraz_submodular(cob.conjuntos, cob.pesos, 5)


def test_verificacion_detecta_violaciones():
    assert todas_cumplen(verificar_seleccion([0, 3, 5], N=6, k=3))
    assert not todas_cumplen(verificar_seleccion([0, 1, 2, 3], N=6, k=3))   # |S| > k
    assert not todas_cumplen(verificar_seleccion([0, 0], N=6, k=3))         # repetido
    assert not todas_cumplen(verificar_seleccion([0, 9], N=6, k=3))         # nodo inexistente
    assert todas_cumplen(verificar_reparto([2, 0, 3], B=5))
    assert not todas_cumplen(verificar_reparto([2, 4], B=5))                # se pasa de B
    assert not todas_cumplen(verificar_reparto([2, -1], B=5))               # negativo
    assert not todas_cumplen(verificar_reparto([1.5, 1], B=5))              # no entero


def test_ronda_cumple_restricciones_y_reparte_optimo():
    """En casos pequeños el reparto entre los elegidos es el óptimo de la DP."""
    for s in range(30):
        N, k, B = 12, 4, 15
        cob = instancia_cobertura(N, 40, 5, semilla=s)
        us = instancia_reparto(N, B, semilla=s).utilidades
        r = resolver_ronda(cob.conjuntos, cob.pesos, k, us, B)
        assert r["cumple_todo"], r["verificaciones"]
        assert len(r["seleccion"]) == k and sum(r["reparto"].values()) == B
        _, optimo = exacto_dp([us[i] for i in r["seleccion"]], B)
        assert math.isclose(r["utilidad_reparto"], optimo)
        # la traza del reparto usa los ids originales de los nodos
        assert {t["nodo"] for t in r["traza_reparto"]} <= set(r["seleccion"])
        assert sum(fila["unidades"] for fila in r["resumen_reparto"]) == B
