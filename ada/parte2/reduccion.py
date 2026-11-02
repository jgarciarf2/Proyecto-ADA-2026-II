"""
Parte 2 — La reducción de NP-dureza, en código (docs/02_parte2.md §3).
"""


def reducir_desde_cobertura_maxima(universo, subconjuntos, k, t):
    """
    Reducción Cobertura Máxima  ≤p  Selección de participantes (versión decisión).

    Entrada (Cobertura Máxima): universo U, subconjuntos S_1..S_N, enteros k, t.
        Pregunta: ¿hay k subconjuntos cuya unión tenga >= t elementos?
    Salida (nuestro problema): un nodo por subconjunto (D_i = S_i), peso 1 a
        cada elemento, el mismo k y el mismo umbral t.
        Pregunta: ¿hay k nodos con utilidad f >= t?
    Costo de la transformación: O(|U| + sum |S_i|) -> polinomial.
    Devuelve (conjuntos, pesos, k, t).
    """
    indice = {e: j for j, e in enumerate(universo)}          # renombrar elementos a 0..|U|-1
    conjuntos = [frozenset(indice[e] for e in S) for S in subconjuntos]
    pesos = [1.0] * len(universo)
    return conjuntos, pesos, k, t
