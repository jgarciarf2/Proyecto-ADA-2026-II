"""
Parte 2 — Algoritmo exacto de referencia por fuerza bruta (solo para N pequeño).
"""
from itertools import combinations
from math import comb

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


def fuerza_bruta_general(valor, k, candidatos, costos=None, presupuesto=None):
    """
    Óptimo exacto para cualquier utilidad valor(S), con |S| <= k y, si se dan costos,
    Σ costos <= presupuesto. Con costos el óptimo puede usar menos de k nodos, así que
    se prueban todos los tamaños 0..k: T = O(Σ_{j<=k} C(n, j) · tau_f).
    Devuelve (mejor_subconjunto, valor).
    """
    candidatos = sorted(candidatos)
    mejor, mejor_v = [], valor([])
    for j in range(1, min(k, len(candidatos)) + 1):
        for S in combinations(candidatos, j):
            if costos is not None and sum(costos[i] for i in S) > presupuesto:
                continue
            v = valor(S)
            if v > mejor_v:
                mejor, mejor_v = list(S), v
    return mejor, mejor_v


def subconjuntos_a_probar(n, k):
    """Cuántos subconjuntos revisa fuerza_bruta_general: Σ_{j<=k} C(n, j)."""
    return sum(comb(n, j) for j in range(min(k, n) + 1))
