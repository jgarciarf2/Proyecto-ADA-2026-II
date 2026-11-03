"""
Formato de casos y ejecución de un caso.  Uso:  python -m pytest tests
"""
import json

import pytest

from ada.casos import CasoInvalido, caso_sintetico, leer_caso, optimo_si_es_factible
from experimentos.casos import ejecutar_caso


def _caso_minimo(**cambios):
    datos = {"nombre": "mini", "k": 2, "B": 5, "pesos_tipos": [1.0, 2.0, 3.0],
             "nodos": [{"id": "a", "tipos": [0, 1], "utilidad": {"familia": "log", "a": 2}},
                       {"id": "b", "tipos": [2], "utilidad": {"familia": "sqrt", "a": 1}},
                       {"id": "c", "tipos": [1, 2], "utilidad": {"familia": "tabla", "valores": [0, 3, 5, 6]}}]}
    datos.update(cambios)
    return datos


def test_leer_caso_valido():
    caso = leer_caso(_caso_minimo())
    assert caso.N == 3 and caso.M == 3 and caso.k == 2 and caso.B == 5
    assert caso.ids == ["a", "b", "c"]
    assert caso.utilidades[2](10) == 6        # la tabla se queda constante al final


@pytest.mark.parametrize("cambio, mensaje", [
    ({"k": 0}, "k debe"),
    ({"B": -1}, "B debe"),
    ({"pesos_tipos": [1.0, 0.0, 3.0]}, "pesos"),
    ({"nodos": [{"id": "a", "tipos": [7], "utilidad": {"familia": "log", "a": 1}}]}, "tipos fuera"),
    ({"nodos": [{"id": "a", "tipos": [0], "utilidad": {"familia": "tabla", "valores": [0, 1, 3]}}]}, "cóncava"),
    ({"nodos": [{"id": "a", "tipos": [0], "utilidad": {"familia": "cubo", "a": 1}}]}, "familia desconocida"),
])
def test_leer_caso_rechaza_entradas_invalidas(cambio, mensaje):
    with pytest.raises(CasoInvalido, match=mensaje):
        leer_caso(_caso_minimo(**cambio))


def test_ejecutar_caso_devuelve_evidencia_con_ids_originales():
    res = ejecutar_caso(_caso_minimo())
    assert res["cumple_todo"]
    assert set(res["seleccion"]) <= {"a", "b", "c"} and len(res["seleccion"]) == 2
    assert {p["nodo"] for p in res["traza_seleccion"]} == set(res["seleccion"])
    assert res["optimo"] is not None and res["utilidad_conjunta"] >= 0.632 * res["optimo"]["valor"]
    json.dumps(res)                            # se puede guardar como JSON


def test_caso_sintetico_ida_y_vuelta():
    datos = caso_sintetico("x", N=30, M=60, d=6, k=5, B=40, semilla=1)
    caso = leer_caso(json.loads(json.dumps(datos)))
    assert caso.N == 30 and caso.k == 5
    assert optimo_si_es_factible(caso, limite=10) is None     # C(30,5) es demasiado grande
