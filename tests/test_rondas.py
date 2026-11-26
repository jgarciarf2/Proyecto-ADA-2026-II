"""Correctitud de V2: fallas reproducibles, disponibilidad y presupuestos."""
import json
import os

import pytest

from ada.casos_red import caso_red_sintetico, leer_caso_red
from ada.variantes.rondas import generar_fallas, resolver_caso_red_v2


def _caso(N=10, T=4, R=20):
    datos = caso_red_sintetico("v2_prueba", N=N, T=T, k=min(3, N), B=8, P=15,
                               R=R, densidad=0.5, semilla=10)
    return leer_caso_red(datos), datos


def test_fallas_son_reproducibles_y_extremos_correctos():
    assert list(generar_fallas(8, 4, 0.35, 17)) == list(generar_fallas(8, 4, 0.35, 17))
    assert all(not r["caidos"] for r in generar_fallas(8, 4, 0, 17))
    assert all(len(r["caidos"]) == 8 for r in generar_fallas(8, 4, 1, 17))


@pytest.mark.parametrize("p", [-0.1, 1.1])
def test_rechaza_probabilidad_fuera_de_rango(p):
    with pytest.raises(ValueError, match="entre 0 y 1"):
        list(generar_fallas(5, 2, p, 1))


def test_nunca_selecciona_nodos_caidos_y_respeta_presupuestos():
    caso, _ = _caso()
    res = resolver_caso_red_v2(caso, 0.45, semilla_fallas=9, con_optimo=False)
    assert res["cumple_todo"]
    for ronda in res["rondas"]:
        assert not (set(ronda["caidos"]) & set(ronda["seleccion"]))
        assert any(v["restriccion"].endswith("nodos caidos no seleccionados") and v["cumple"]
                   for v in ronda["verificaciones"])
        assert len(ronda["seleccion"]) <= caso.k
        assert ronda["costo_participacion"] <= caso.P
        assert sum(x["unidades"] for x in ronda["reparto"]) <= caso.B
    assert all(x["usado"] <= x["tope"] for x in res["presupuesto_usado"])
    json.dumps(res)


def test_sin_fallas_coincide_con_la_solucion_base():
    from ada.solucion_red import resolver_caso_red

    caso, _ = _caso()
    base = resolver_caso_red(caso, con_optimo=False)
    v2 = resolver_caso_red_v2(caso, 0, semilla_fallas=0, con_optimo=False)
    assert [r["seleccion"] for r in v2["rondas"]] == [r["seleccion"] for r in base["rondas"]]
    assert [r["reparto"] for r in v2["rondas"]] == [r["reparto"] for r in base["rondas"]]


def test_puno_genera_rondas_vacias_sin_gastar_presupuesto():
    caso, _ = _caso()
    res = resolver_caso_red_v2(caso, 1, semilla_fallas=4, con_optimo=False)
    assert res["cumple_todo"]
    assert all(r["seleccion"] == [] and r["reparto"] == [] for r in res["rondas"])
    assert all(len(r["caidos"]) == caso.N for r in res["rondas"])
    assert all(x["usado"] == 0 for x in res["presupuesto_usado"])


def test_ronda_intermedia_con_todos_caidos_no_selecciona_ni_gasta():
    caso, _ = _caso(N=10, T=4)
    res = resolver_caso_red_v2(caso, 0.5, semilla_fallas=540, con_optimo=False)
    ronda = res["rondas"][2]
    assert len(ronda["caidos"]) == caso.N
    assert ronda["seleccion"] == []
    assert ronda["reparto"] == []
    assert ronda["costo_participacion"] == 0
    assert ronda["cumple_todo"]
