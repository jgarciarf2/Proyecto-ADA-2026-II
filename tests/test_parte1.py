"""
Correctitud de la Parte 1.  Uso:  python -m pytest tests
"""
import math

from ada.generadores import instancia_reparto
from ada.parte1 import ContadorComparaciones, exacto_dp, voraz_heap
from ada.utilidades import Utilidad, UtilidadLog


def test_voraz_igual_al_optimo_dp():
    """En 300 instancias pequeñas (N <= 7, B <= 25) el voraz iguala al verificador DP."""
    for s in range(300):
        N = 2 + s % 6
        B = 1 + (s * 7) % 25
        inst = instancia_reparto(N, B, semilla=s)
        _, v_voraz = voraz_heap(inst.utilidades, inst.B)
        _, v_exacto = exacto_dp(inst.utilidades, inst.B)
        assert abs(v_voraz - v_exacto) <= 1e-9, f"semilla={s}"


def test_reparto_respeta_el_presupuesto():
    inst = instancia_reparto(50, 1000, semilla=7)
    x, total = voraz_heap(inst.utilidades, inst.B)
    assert sum(x) == inst.B
    assert all(xi >= 0 for xi in x)
    assert math.isclose(total, sum(u(xi) for u, xi in zip(inst.utilidades, x)))


def test_contador_no_cambia_el_resultado_y_respeta_cotas():
    """Con contador el algoritmo es el mismo, y las comparaciones caben en 2N y 2·B·log2 N."""
    N, B = 1024, 20 * 1024
    inst = instancia_reparto(N, B, semilla=N)
    c = ContadorComparaciones()
    assert voraz_heap(inst.utilidades, inst.B, contador=c) == voraz_heap(inst.utilidades, inst.B)
    assert 0 < c.heapify <= 2 * N
    assert 0 < c.pasos <= 2 * B * math.log2(N)


class _NoConcava(Utilidad):
    """u(0) = 0, u(1) = 0, u(2) = 10: no cóncava."""
    def __call__(self, x):
        return 10.0 if x >= 2 else 0.0


def test_sin_concavidad_el_voraz_falla():
    """Contraejemplo de docs/01 §2.3: la concavidad es necesaria."""
    us = [UtilidadLog(1.0), _NoConcava()]
    _, v_voraz = voraz_heap(us, 2)
    _, v_exacto = exacto_dp(us, 2)
    assert v_exacto == 10.0
    assert v_voraz < v_exacto
