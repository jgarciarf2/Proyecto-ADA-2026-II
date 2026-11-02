"""
Parte 2 — Utilidad de cobertura ponderada (monótona y submodular, Lema 1 de
docs/02_parte2.md).
"""


def f(S, conjuntos, pesos):
    """Utilidad conjunta de un subconjunto S de nodos. Costo O(sum |D_i|)."""
    cubiertos = set()
    for i in S:
        cubiertos |= conjuntos[i]
    return sum(pesos[e] for e in cubiertos)


def ganancia_marginal(i, cubiertos, conjuntos, pesos):
    """
    f(S ∪ {i}) - f(S), sabiendo qué tipos ya cubre S.
    Recorre los d elementos de D_i con búsqueda O(1) en un set: tau = O(d).
    """
    return sum(pesos[e] for e in conjuntos[i] if e not in cubiertos)
