"""
Parte 1 — Reparto óptimo del presupuesto.

Entrada: N utilidades cóncavas crecientes u_1..u_N y un presupuesto entero B.
Salida:  x_1..x_N enteros >= 0 con sum x_i <= B que maximiza sum u_i(x_i).

Dos algoritmos:
  * voraz_heap  -> el algoritmo del proyecto, O(N + B log N).
  * exacto_dp   -> verificador independiente por programación dinámica,
                   O(N * B^2). Solo sirve para comprobar en instancias
                   pequeñas que el voraz da el óptimo (no es la solución
                   que se entrega: el enunciado prohíbe fuerza bruta aquí).
"""
import heapq


def voraz_heap(utilidades, B, contar=False):
    """
    Entrega una unidad a la vez al nodo de mayor ganancia marginal.

    Costo (contando operaciones):
      - construir la lista de N ganancias iniciales:    N evaluaciones -> O(N)
      - heapify:                                         O(N)
      - B iteraciones, cada una:
            mirar el máximo (raíz)                       O(1)
            1 evaluación de la nueva ganancia            O(1)
            heapreplace (sustituir raíz y hundirla)      O(log N)
      Total: T(N, B) = O(N) + B * O(log N) = O(N + B log N)
    """
    N = len(utilidades)
    x = [0] * N
    # heapq es un montículo de mínimos: guardamos -ganancia para tener el máximo arriba.
    heap = [(-u.marginal(0), i) for i, u in enumerate(utilidades)]
    heapq.heapify(heap)
    total = 0.0
    pasos = 0
    for _ in range(B):
        neg_g, i = heap[0]
        if -neg_g <= 0:          # ninguna unidad extra aporta: parar (sum x_i <= B)
            break
        x[i] += 1
        total += -neg_g
        heapq.heapreplace(heap, (-utilidades[i].marginal(x[i]), i))
        pasos += 1
    if contar:
        return x, total, pasos
    return x, total


def exacto_dp(utilidades, B):
    """
    Verificador exacto: mejor[b] = mejor utilidad usando los primeros i nodos
    y a lo sumo b unidades. Recurrencia:
        mejor_i[b] = max_{0 <= t <= b} ( mejor_{i-1}[b - t] + u_i(t) )
    Costo O(N * B^2). No asume concavidad, por eso sirve como juez imparcial.
    """
    N = len(utilidades)
    mejor = [0.0] * (B + 1)
    eleccion = []
    for u in utilidades:
        valores = [u(t) for t in range(B + 1)]
        nuevo = [0.0] * (B + 1)
        arg = [0] * (B + 1)
        for b in range(B + 1):
            m, am = -1.0, 0
            for t in range(b + 1):
                v = mejor[b - t] + valores[t]
                if v > m:
                    m, am = v, t
            nuevo[b], arg[b] = m, am
        mejor = nuevo
        eleccion.append(arg)
    # reconstrucción hacia atrás
    x = [0] * N
    b = B
    for i in range(N - 1, -1, -1):
        x[i] = eleccion[i][b]
        b -= x[i]
    return x, mejor[B]


# ---------------------------------------------------------------------------
# Versión instrumentada: cuenta comparaciones del montículo.
# Sirve para validar T(N,B) contando operaciones (independiente de la máquina,
# sin efectos de caché ni del intérprete).
# ---------------------------------------------------------------------------
class _Item:
    __slots__ = ("clave", "i")
    comparaciones = 0

    def __init__(self, clave, i):
        self.clave, self.i = clave, i

    def __lt__(self, otro):
        _Item.comparaciones += 1
        return (self.clave, self.i) < (otro.clave, otro.i)


def voraz_heap_contando(utilidades, B):
    """Mismo algoritmo que voraz_heap; devuelve (comparaciones_heapify, comparaciones_pasos)."""
    _Item.comparaciones = 0
    x = [0] * len(utilidades)
    heap = [_Item(-u.marginal(0), i) for i, u in enumerate(utilidades)]
    heapq.heapify(heap)
    c_heapify = _Item.comparaciones
    for _ in range(B):
        top = heap[0]
        if -top.clave <= 0:
            break
        x[top.i] += 1
        heapq.heapreplace(heap, _Item(-utilidades[top.i].marginal(x[top.i]), top.i))
    return c_heapify, _Item.comparaciones - c_heapify
