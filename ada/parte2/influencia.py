"""
Parte 2 con el formato de la profesora: utilidad conjunta por influencia en un grafo.

Cada nodo v tiene un coeficiente a_v > 0 y cada arista {u, v} un peso de influencia
w_uv en [0, 1]. Tomamos w_vv = 1 (un nodo elegido se cuenta completo) y

    f(S) = Σ_v a_v · (1 − Π_{u∈S} (1 − w_uv))

es decir, cada nodo v aporta a_v multiplicado por la probabilidad de que al menos un
nodo de S lo influya. Es una cobertura probabilística: f(∅) = 0, es monótona (agregar
u solo multiplica el producto por (1 − w_uv) <= 1) y submodular (la ganancia de agregar
i es Σ_v a_v · q_v · w_iv con q_v = Π_{u∈S}(1 − w_uv), y q_v solo baja cuando S crece).
Por eso el voraz conserva la cota (1 − 1/e) cuando la única restricción es |S| <= k.

SUPUESTO PROVISIONAL: la profesora no ha confirmado esta fórmula.
"""
from ada.parte2.voraz import voraz_general


def matriz_influencia(N, aristas):
    """aristas = [(u, v, w)] con índices 0..N-1. Grafo no dirigido, diagonal 1. Costo O(N² + |E|)."""
    W = [[0.0] * N for _ in range(N)]
    for u, v, w in aristas:
        W[u][v] = W[v][u] = w
    for v in range(N):
        W[v][v] = 1.0
    return W


def f_influencia(S, a, W):
    """Utilidad conjunta de S. Costo O(N · |S|)."""
    total = 0.0
    for v in range(len(a)):
        q = 1.0
        for u in S:
            q *= 1.0 - W[u][v]
        total += a[v] * (1.0 - q)
    return total


class EstadoInfluencia:
    """
    Guarda q_v = Π_{u∈S}(1 − w_uv) para el S actual.
    ganancia(i) = Σ_v a_v · q_v · w_iv     -> tau = O(N)
    agregar(j): q_v *= (1 − w_jv)           -> O(N)
    """

    def __init__(self, a, W):
        self.a, self.W = a, W
        self.q = [1.0] * len(a)

    def ganancia(self, i):
        fila = self.W[i]
        return sum(av * qv * w for av, qv, w in zip(self.a, self.q, fila))

    def agregar(self, j):
        fila = self.W[j]
        self.q = [qv * (1.0 - w) for qv, w in zip(self.q, fila)]


def voraz_influencia(a, W, k, candidatos=None, costos=None, presupuesto=None, contar=False, traza=None):
    """
    Voraz sobre f_influencia. Con n candidatos: T(n, k) = O(n · k · N), porque cada
    evaluación de la ganancia recorre los N nodos. Si además hay costos, solo se
    consideran los nodos cuyo costo cabe en el presupuesto de participación.
    """
    estado = EstadoInfluencia(a, W)
    return voraz_general(len(a), k, estado.ganancia, estado.agregar, candidatos=candidatos,
                         costos=costos, presupuesto=presupuesto, contar=contar, traza=traza)
