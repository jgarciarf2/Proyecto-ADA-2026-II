"""
Parte 2 — Voraz submodular: aproximación (1 - 1/e) (Nemhauser, Wolsey y Fisher, 1978).

Hay un solo voraz (voraz_general) que trabaja sobre cualquier utilidad monótona y
submodular, dada por dos funciones: ganancia(i) y agregar(i). voraz_submodular es
el mismo voraz con la utilidad de cobertura ponderada.
"""
from ada.parte2.cobertura import ganancia_marginal


def voraz_general(N, k, ganancia, agregar, candidatos=None, costos=None, presupuesto=None,
                  contar=False, traza=None):
    """
    En cada paso (como mucho k) agrega el candidato de mayor ganancia marginal.

    ganancia(i)  -> f(S ∪ {i}) - f(S) para el S actual (costo tau)
    agregar(i)   -> actualiza el estado interno de la utilidad con S := S ∪ {i}
    candidatos   -> nodos que se pueden elegir (por defecto 0..N-1)
    costos, presupuesto -> si se dan, solo se evalúan los nodos cuyo costo todavía
                           cabe: Σ_{i∈S} costos[i] <= presupuesto. Con costos la cota
                           (1 - 1/e) ya no está garantizada (es la variante V1).

    Devuelve (elegidos, valor) o, con contar=True, (elegidos, valor, evaluaciones).
    Si se pasa una lista en traza, se le agrega un registro por paso:
    {"paso", "nodo", "ganancia_marginal", "utilidad_acumulada", "candidatos_evaluados"}
    y, con costos, también "costo_acumulado".

    Conteo (n = número de candidatos):
      paso t: evalúa como mucho n - t candidatos, cada uno con costo tau
      Evaluaciones totales <= sum_{t=0}^{k-1} (n - t) = kn - k(k-1)/2 <= n k
      T(n, k) = O(n · k · tau)
    """
    restantes = set(range(N)) if candidatos is None else set(candidatos)
    elegidos, valor, evaluaciones, gastado = [], 0.0, 0, 0
    for paso in range(min(k, len(restantes))):
        mejor, mejor_g, evaluados = None, -1.0, 0
        for i in restantes:
            if costos is not None and gastado + costos[i] > presupuesto:
                continue
            g = ganancia(i)
            evaluados += 1
            if g > mejor_g or (g == mejor_g and i < mejor):
                mejor, mejor_g = i, g
        evaluaciones += evaluados
        if mejor is None:                 # ningún candidato cabe en el presupuesto
            break
        elegidos.append(mejor)
        restantes.remove(mejor)
        agregar(mejor)
        valor += mejor_g
        if costos is not None:
            gastado += costos[mejor]
        if traza is not None:
            registro = {"paso": paso + 1, "nodo": mejor, "ganancia_marginal": mejor_g,
                        "utilidad_acumulada": valor, "candidatos_evaluados": evaluados}
            if costos is not None:
                registro["costo_acumulado"] = gastado
            traza.append(registro)
    if contar:
        return elegidos, valor, evaluaciones
    return elegidos, valor


def voraz_submodular(conjuntos, pesos, k, contar=False, traza=None):
    """
    Voraz con la utilidad de cobertura ponderada.

    Conteo:
      paso t (t = 0..k-1): evalúa la ganancia de los N - t nodos restantes,
                           cada evaluación cuesta tau = O(d)
                           + actualizar 'cubiertos' con el elegido: O(d)
      Evaluaciones totales: sum_{t=0}^{k-1} (N - t) = kN - k(k-1)/2  <= N k
      T(N, k) = O(N · k · tau) = O(N · k · d)
    """
    cubiertos = set()
    return voraz_general(len(conjuntos), k,
                         ganancia=lambda i: ganancia_marginal(i, cubiertos, conjuntos, pesos),
                         agregar=lambda j: cubiertos.update(conjuntos[j]),
                         contar=contar, traza=traza)
