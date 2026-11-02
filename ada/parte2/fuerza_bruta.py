"""
Parte 2 — Algoritmo exacto de referencia por fuerza bruta (solo para N pequeño).
"""
from itertools import combinations

from ada.parte2.cobertura import f


def fuerza_bruta(conjuntos, pesos, k):
    """
    Prueba los C(N, k) subconjuntos de tamaño k (por monotonía, el óptimo
    siempre se alcanza con exactamente k nodos). Cada evaluación de f cuesta
    O(k·d), así que T(N, k) = O(C(N,k) · k · d): exponencial en k.
    Devuelve (mejor_subconjunto, valor).
    """
    N = len(conjuntos)
    k = min(k, N)
    mejor, mejor_v = None, -1.0
    for S in combinations(range(N), k):
        v = f(S, conjuntos, pesos)
        if v > mejor_v:
            mejor, mejor_v = list(S), v
    return mejor, mejor_v
