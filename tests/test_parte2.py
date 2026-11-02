"""
Correctitud de la Parte 2.  Uso:  python -m pytest tests
"""
import math
import random

from ada.generadores import instancia_cobertura, instancia_cobertura_dificil
from ada.parte2 import f, fuerza_bruta, reducir_desde_cobertura_maxima, voraz_submodular

COTA = 1 - 1 / math.e


def test_cobertura_es_monotona_y_submodular():
    """Lema 1 de docs/02: 2 000 pruebas aleatorias con A ⊆ A' y v ∉ A'."""
    rng = random.Random(1)
    inst = instancia_cobertura(12, 30, 6, semilla=1)
    C, w = inst.conjuntos, inst.pesos
    for _ in range(2000):
        A2 = set(rng.sample(range(12), rng.randint(0, 11)))   # A'
        A = set(x for x in A2 if rng.random() < 0.5)            # A ⊆ A'
        resto = [v for v in range(12) if v not in A2]
        if not resto:
            continue
        v = rng.choice(resto)
        fA, fA2 = f(A, C, w), f(A2, C, w)
        assert fA <= fA2 + 1e-9
        assert (f(A | {v}, C, w) - fA) >= (f(A2 | {v}, C, w) - fA2) - 1e-9


def test_voraz_respeta_la_cota():
    """Voraz >= (1 - 1/e) · óptimo en 200 instancias con mucho traslape."""
    for s in range(200):
        rng = random.Random(s)
        N, k, M = rng.randint(6, 12), rng.randint(2, 4), rng.randint(8, 20)
        inst = instancia_cobertura_dificil(N, M, s)
        _, v_voraz = voraz_submodular(inst.conjuntos, inst.pesos, k)
        _, v_opt = fuerza_bruta(inst.conjuntos, inst.pesos, k)
        assert v_voraz >= COTA * v_opt - 1e-9, f"semilla={s}"


def test_evaluaciones_coinciden_con_la_formula():
    """E(N, k) = kN - k(k-1)/2 exactamente."""
    for N, k in [(50, 1), (50, 10), (200, 37)]:
        inst = instancia_cobertura(N, 300, 5, semilla=N + k)
        _, _, ev = voraz_submodular(inst.conjuntos, inst.pesos, k, contar=True)
        assert ev == k * N - k * (k - 1) // 2


def test_ejemplo_de_la_reduccion():
    """Ejemplo de docs/02 §3 y §5.3: el voraz da 5 y el óptimo 6."""
    U = [1, 2, 3, 4, 5, 6]
    S = [{1, 2, 3}, {4, 5, 6}, {1, 2, 4, 5}]
    conjuntos, pesos, k, t = reducir_desde_cobertura_maxima(U, S, k=2, t=6)
    assert pesos == [1.0] * 6
    elegidos, v_voraz = voraz_submodular(conjuntos, pesos, k)
    assert elegidos[0] == 2 and v_voraz == 5
    opt, v_opt = fuerza_bruta(conjuntos, pesos, k)
    assert sorted(opt) == [0, 1] and v_opt >= t
