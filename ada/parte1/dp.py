"""
Parte 1 — Verificador exacto por programación dinámica.

Solo sirve para comprobar en instancias pequeñas que el voraz da el óptimo.
No es la solución que se entrega: el enunciado pide el voraz, no fuerza bruta.
"""


def exacto_dp(utilidades, B):
    """
    mejor[b] = mejor utilidad usando los primeros i nodos y a lo sumo b unidades.
    Recurrencia:
        mejor_i[b] = max_{0 <= t <= b} ( mejor_{i-1}[b - t] + u_i(t) )
    Costo O(N * B^2). No asume concavidad, por eso sirve como juez imparcial.
    Devuelve (x, utilidad_total).
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
