"""
Variante V1 — costos de participación: |S| <= k y Σ_{i∈S} c_i <= P (docs/03_variantes.md).

Dos algoritmos con garantía cuando el cupo k no restringe (k >= k_max(P)):
  algoritmo_a: voraz por razón Δ/c + mejor nodo individual   -> ½(1 − 1/e)  (Krause y Guestrin, 2005)
  algoritmo_b: enumeración parcial de 3 nodos + voraz por razón -> (1 − 1/e)  (Sviridenko, 2004)
Si el cupo sí restringe: A >= f(O)/k y B >= f(O)/⌈k/3⌉ (Teorema V1.4).
"""
from itertools import combinations

from ada.parte2.influencia import EstadoInfluencia, f_influencia, voraz_influencia


def k_max(costos, P, candidatos=None):
    """
    Máximo número de nodos que caben en P: se toman los más baratos mientras quepan.
    Ordenar cuesta O(n log n) y recorrer, O(n).
    """
    candidatos = range(len(costos)) if candidatos is None else candidatos
    gastado, cuenta = 0, 0
    for c in sorted(costos[i] for i in candidatos):
        if gastado + c > P:
            break
        gastado, cuenta = gastado + c, cuenta + 1
    return cuenta


def _factibles(costos, P, candidatos):
    """Descarta los nodos que no caben solos en P (no están en ningún grupo factible). O(n)."""
    candidatos = range(len(costos)) if candidatos is None else candidatos
    return [i for i in candidatos if costos[i] <= P]


def algoritmo_a(a, W, k, costos, P, candidatos=None, contar=False):
    """
    ALGORITMO-A (sección V1.5): el mejor entre el voraz por razón y el mejor nodo solo.

    Con n candidatos y m = min(k, k_max(P)) <= n pasos:
      voraz por razón: paso t evalúa <= n - t ganancias de costo O(N)  -> O(n · m · N)
      mejor nodo solo: n utilidades f({i}) = Σ_v a_v w_iv de costo O(N) -> O(n · N)
      T_A(N, k) = O(N² · k)   (n <= N), el mismo orden que el voraz de la solución base.
    Devuelve (S, valor) o, con contar=True, (S, valor, evaluaciones de la ganancia).
    """
    V = _factibles(costos, P, candidatos)
    S, valor, evaluaciones = voraz_influencia(a, W, k, candidatos=V, costos=costos, presupuesto=P,
                                              contar=True, razon=True)
    if V:
        solo = max(V, key=lambda i: (f_influencia([i], a, W), -i))
        valor_solo = f_influencia([solo], a, W)
        evaluaciones += len(V)
        if valor_solo > valor:
            S, valor = [solo], valor_solo
    return (S, valor, evaluaciones) if contar else (S, valor)


def algoritmo_b(a, W, k, costos, P, candidatos=None, contar=False):
    """
    ALGORITMO-B (sección V1.6): prueba los grupos factibles de 1 y 2 nodos y completa
    cada grupo factible de 3 nodos con el voraz por razón.

    Con n candidatos:
      grupos de 1 y 2: O(n²) grupos, cada f(G) cuesta O(N)               -> O(n² · N)
      grupos de 3: C(n, 3) = O(n³) arranques; preparar q cuesta O(N) y
                   completar con el voraz, O(n · k · N)                  -> O(n³ · n · k · N)
      T_B(N, k) = O(N⁵ · k)
    Si k <= 3 revisa todos los grupos factibles y es exacto.
    Devuelve (S, valor) o, con contar=True, (S, valor, evaluaciones de la ganancia).
    """
    V = _factibles(costos, P, candidatos)
    mejor, mejor_v, evaluaciones = [], 0.0, 0
    for tam in (1, 2):
        if tam > k:
            break
        for G in combinations(V, tam):
            if sum(costos[i] for i in G) <= P:
                v = f_influencia(list(G), a, W)
                evaluaciones += 1
                if v > mejor_v:
                    mejor, mejor_v = list(G), v
    if k >= 3:
        for G in combinations(V, 3):
            costo_G = sum(costos[i] for i in G)
            if costo_G > P:
                continue
            estado = EstadoInfluencia(a, W)
            for i in G:
                estado.agregar(i)
            resto = [i for i in V if i not in G]
            S, extra, ev = voraz_influencia(a, W, k - 3, candidatos=resto, costos=costos,
                                            presupuesto=P - costo_G, contar=True, razon=True, estado=estado)
            v = f_influencia(list(G), a, W) + extra       # el voraz devuelve solo lo que agrega a f(G)
            evaluaciones += ev + 1
            if v > mejor_v:
                mejor, mejor_v = list(G) + S, v
    return (mejor, mejor_v, evaluaciones) if contar else (mejor, mejor_v)
