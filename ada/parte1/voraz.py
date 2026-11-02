"""
Parte 1 — Voraz con montículo: entrega una unidad a la vez al nodo de mayor
ganancia marginal. Es óptimo cuando las utilidades son cóncavas (argumento de
intercambio en docs/01_formalizacion_y_parte1.md §2.3).
"""
import heapq


def voraz_heap(utilidades, B, contador=None):
    """
    Devuelve (x, utilidad_total).

    Costo (contando operaciones):
      - construir la lista de N ganancias iniciales:    N evaluaciones -> O(N)
      - heapify:                                         O(N)
      - B iteraciones, cada una:
            mirar el máximo (raíz)                       O(1)
            1 evaluación de la nueva ganancia            O(1)
            heapreplace (sustituir raíz y hundirla)      O(log N)
      Total: T(N, B) = O(N) + B * O(log N) = O(N + B log N)

    Si se pasa un ContadorComparaciones, el mismo algoritmo cuenta cuántas
    comparaciones hace el montículo (para validar T contando operaciones).
    """
    par = tuple if contador is None else contador.par
    N = len(utilidades)
    x = [0] * N
    # heapq es un montículo de mínimos: guardamos -ganancia para tener el máximo arriba.
    heap = [par((-u.marginal(0), i)) for i, u in enumerate(utilidades)]
    heapq.heapify(heap)
    if contador is not None:
        contador.fin_heapify()
    total = 0.0
    for _ in range(B):
        neg_g, i = heap[0]
        if -neg_g <= 0:          # ninguna unidad extra aporta: parar (sum x_i <= B)
            break
        x[i] += 1
        total += -neg_g
        heapq.heapreplace(heap, par((-utilidades[i].marginal(x[i]), i)))
    return x, total


class ContadorComparaciones:
    """
    Cuenta las comparaciones del montículo, separadas en heapify y pasos.
    Es independiente de la máquina: no le afectan la caché ni el intérprete.

    Funciona porque heapq compara los elementos con '<'; aquí los pares son
    tuplas cuyo '<' suma 1 al contador antes de comparar.
    """

    def __init__(self):
        self.total = 0
        self.heapify = 0
        contador = self

        class _Par(tuple):
            __slots__ = ()

            def __lt__(self, otro):
                contador.total += 1
                return tuple.__lt__(self, otro)

        self.par = _Par

    def fin_heapify(self):
        self.heapify = self.total

    @property
    def pasos(self):
        return self.total - self.heapify
