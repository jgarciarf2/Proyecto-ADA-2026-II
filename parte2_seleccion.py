"""
Parte 2 — Selección de nodos participantes.

Entrada: N nodos; el nodo i cubre el conjunto D_i de "tipos de datos";
         cada tipo e tiene peso w_e; un cupo k.
Utilidad conjunta (cobertura ponderada): f(S) = sum_{e in U_{i in S} D_i} w_e
Objetivo: elegir S con |S| <= k que maximice f(S).

Contenido:
  * f, ganancia_marginal           -> la función de utilidad (tau = O(d))
  * voraz_submodular               -> aproximación (1 - 1/e), O(N k d)
  * fuerza_bruta                   -> óptimo exacto, O(C(N,k) k d), solo para N pequeño
  * reducir_desde_cobertura_maxima -> la reducción de NP-dureza, en código
"""
from itertools import combinations


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


def voraz_submodular(conjuntos, pesos, k, contar=False):
    """
    En cada uno de los k pasos agrega el nodo con mayor ganancia marginal.

    Conteo:
      paso t (t = 0..k-1): evalúa la ganancia de los N - t nodos restantes,
                           cada evaluación cuesta tau = O(d)
                           + actualizar 'cubiertos' con el elegido: O(d)
      Evaluaciones totales: sum_{t=0}^{k-1} (N - t) = kN - k(k-1)/2  <= N k
      T(N, k) = O(N · k · tau) = O(N · k · d)
    """
    N = len(conjuntos)
    elegidos, restantes = [], set(range(N))
    cubiertos = set()
    valor = 0.0
    evaluaciones = 0
    for _ in range(min(k, N)):
        mejor, mejor_g = None, -1.0
        for i in restantes:
            g = ganancia_marginal(i, cubiertos, conjuntos, pesos)
            evaluaciones += 1
            if g > mejor_g or (g == mejor_g and i < mejor):
                mejor, mejor_g = i, g
        elegidos.append(mejor)
        restantes.remove(mejor)
        cubiertos |= conjuntos[mejor]
        valor += mejor_g
    if contar:
        return elegidos, valor, evaluaciones
    return elegidos, valor


def fuerza_bruta(conjuntos, pesos, k):
    """
    Prueba los C(N, k) subconjuntos de tamaño k (por monotonía, el óptimo
    siempre se alcanza con exactamente k nodos). Cada evaluación de f cuesta
    O(k·d), así que T(N, k) = O(C(N,k) · k · d): exponencial en k.
    """
    N = len(conjuntos)
    k = min(k, N)
    mejor, mejor_v = None, -1.0
    for S in combinations(range(N), k):
        v = f(S, conjuntos, pesos)
        if v > mejor_v:
            mejor, mejor_v = list(S), v
    return mejor, mejor_v


def reducir_desde_cobertura_maxima(universo, subconjuntos, k, t):
    """
    Reducción Cobertura Máxima  ≤p  Selección de participantes (versión decisión).

    Entrada (Cobertura Máxima): universo U, subconjuntos S_1..S_N, enteros k, t.
        Pregunta: ¿hay k subconjuntos cuya unión tenga >= t elementos?
    Salida (nuestro problema): un nodo por subconjunto (D_i = S_i), peso 1 a
        cada elemento, el mismo k y el mismo umbral t.
        Pregunta: ¿hay k nodos con utilidad f >= t?
    Costo de la transformación: O(|U| + sum |S_i|) -> polinomial.
    """
    indice = {e: j for j, e in enumerate(universo)}          # renombrar elementos a 0..|U|-1
    conjuntos = [frozenset(indice[e] for e in S) for S in subconjuntos]
    pesos = [1.0] * len(universo)
    return conjuntos, pesos, k, t
