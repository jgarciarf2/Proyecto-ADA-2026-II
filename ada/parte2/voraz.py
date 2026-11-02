"""
Parte 2 — Voraz submodular: aproximación (1 - 1/e) (Nemhauser, Wolsey y Fisher, 1978).
"""
from ada.parte2.cobertura import ganancia_marginal


def voraz_submodular(conjuntos, pesos, k, contar=False, traza=None):
    """
    En cada uno de los k pasos agrega el nodo con mayor ganancia marginal.
    Devuelve (elegidos, valor) o, con contar=True, (elegidos, valor, evaluaciones).
    Si se pasa una lista en traza, se le agrega un registro por paso:
    {"paso", "nodo", "ganancia_marginal", "utilidad_acumulada", "candidatos_evaluados"}.

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
    for paso in range(min(k, N)):
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
        if traza is not None:
            traza.append({"paso": paso + 1, "nodo": mejor, "ganancia_marginal": mejor_g,
                          "utilidad_acumulada": valor, "candidatos_evaluados": N - paso})
    if contar:
        return elegidos, valor, evaluaciones
    return elegidos, valor
