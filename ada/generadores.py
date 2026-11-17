"""
Generación de instancias sintéticas (reproducibles con semilla fija).

Todas las instancias del proyecto salen de aquí, para que experimentos,
pruebas y variantes usen exactamente los mismos datos.
"""
import random

from ada.modelo import InstanciaCobertura, InstanciaCostos, InstanciaInfluencia, InstanciaReparto
from ada.parte2.influencia import matriz_influencia
from ada.utilidades import UtilidadLog, UtilidadRaiz, UtilidadSaturacion


def instancia_reparto(N, B, semilla=0):
    """Parte 1: N utilidades cóncavas de familias y parámetros al azar, y un presupuesto B."""
    rng = random.Random(semilla)
    utilidades = []
    for _ in range(N):
        tipo = rng.choice(["log", "sqrt", "exp"])
        a = rng.uniform(1.0, 10.0)
        b = rng.uniform(0.05, 0.5)          # se sortea siempre, aunque solo lo use "exp"
        if tipo == "log":
            utilidades.append(UtilidadLog(a))
        elif tipo == "sqrt":
            utilidades.append(UtilidadRaiz(a))
        else:
            utilidades.append(UtilidadSaturacion(a, b))
    return InstanciaReparto(utilidades, B)


# ---------------------------------------------------------------------------
# Parte 2: utilidad conjunta de COBERTURA PONDERADA.
# Hay un universo de M "tipos de datos" (0..M-1), cada uno con peso w_e > 0.
# El nodo i aporta datos de un subconjunto D_i del universo.
# f(S) = suma de los pesos de los tipos cubiertos por al menos un nodo de S.
# ---------------------------------------------------------------------------
def instancia_cobertura(N, M, d, semilla=0):
    """N nodos, universo de M tipos, cada nodo cubre exactamente d tipos al azar."""
    rng = random.Random(semilla)
    pesos = [rng.uniform(1.0, 10.0) for _ in range(M)]
    conjuntos = [frozenset(rng.sample(range(M), d)) for _ in range(N)]
    return InstanciaCobertura(conjuntos, pesos)


def instancia_cobertura_dificil(N, M, semilla=0):
    """Universo pequeño y tamaños variables: mucho traslape, donde el voraz más se equivoca."""
    rng = random.Random(semilla)
    pesos = [rng.uniform(1, 10) for _ in range(M)]
    conjuntos = [frozenset(rng.sample(range(M), rng.randint(1, max(2, M // 3)))) for _ in range(N)]
    return InstanciaCobertura(conjuntos, pesos)


def instancia_influencia(N, semilla=0, densidad=1.0):
    """
    N nodos con coeficiente a en [1, 10], costo entero en [1, 7] y, para cada par de
    nodos, una arista con probabilidad 'densidad' y peso de influencia en [0.05, 0.9].
    Con densidad = 1 el grafo es completo, como en el caso de la profesora.
    """
    rng = random.Random(semilla)
    a = [rng.uniform(1.0, 10.0) for _ in range(N)]
    costos = [rng.randint(1, 7) for _ in range(N)]
    aristas = [(u, v, round(rng.uniform(0.05, 0.9), 2)) for u in range(N) for v in range(u + 1, N)
               if rng.random() < densidad]
    return InstanciaInfluencia(a, matriz_influencia(N, aristas), costos)


def instancia_costos(N, semilla=0, densidad=0.5, regimen="presupuesto"):
    """
    Instancia de la variante V1 sobre instancia_influencia (mismos a, W y costos en [1, 7]).
    P es una fracción al azar (entre 30 % y 60 %) de la suma de los costos.
      regimen = "presupuesto": k = N, así que el cupo nunca restringe (k >= k_max(P)).
      regimen = "mixto":       k < k_max(P), así que las dos restricciones pueden estar activas.
    Usa un generador aparte (semilla + 1) para no cambiar los números de instancia_influencia.
    """
    from ada.variantes.costos import k_max          # import local: variantes depende de parte2, no al revés
    base = instancia_influencia(N, semilla, densidad)
    rng = random.Random(semilla + 1)
    P = max(1, int(sum(base.costos) * rng.uniform(0.3, 0.6)))
    tope = k_max(base.costos, P)
    if regimen == "mixto" and tope >= 2:
        k = rng.randint(min(2, tope - 1), tope - 1)       # k = 1 sería trivial (basta el mejor nodo)
    elif regimen == "mixto":
        raise ValueError("con estos costos no hay un k que restrinja: pruebe otra semilla o un N mayor")
    else:
        k = N
    return InstanciaCostos(base.a, base.W, base.costos, k, P, regimen)
