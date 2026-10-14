"""
Generación de instancias sintéticas (reproducibles con semilla fija).

Parte 1: cada nodo i tiene una utilidad u_i(x) definida sobre enteros x >= 0,
creciente y cóncava. Usamos tres familias clásicas, todas con u_i(0) = 0:

    log:   u(x) = a * ln(1 + x)
    sqrt:  u(x) = a * sqrt(x)
    exp:   u(x) = a * (1 - e^{-b x})      (saturación)

En las tres, la ganancia marginal g(x) = u(x+1) - u(x) es positiva y no
creciente en x, que es exactamente la definición de cóncava en enteros.
"""
import math
import random


class Utilidad:
    """Utilidad cóncava y creciente de un nodo. Evaluarla cuesta O(1)."""

    __slots__ = ("tipo", "a", "b")

    def __init__(self, tipo, a, b=1.0):
        self.tipo, self.a, self.b = tipo, a, b

    def __call__(self, x):
        if self.tipo == "log":
            return self.a * math.log1p(x)
        if self.tipo == "sqrt":
            return self.a * math.sqrt(x)
        if self.tipo == "exp":
            return self.a * (1.0 - math.exp(-self.b * x))
        raise ValueError(self.tipo)

    def marginal(self, x):
        """Ganancia de dar la unidad número x+1: u(x+1) - u(x)."""
        return self(x + 1) - self(x)

    def __repr__(self):
        return f"Utilidad({self.tipo}, a={self.a:.2f}, b={self.b:.2f})"


def instancia_reparto(N, B, semilla=0):
    """Instancia de la Parte 1: N utilidades cóncavas y un presupuesto B."""
    rng = random.Random(semilla)
    utilidades = []
    for _ in range(N):
        tipo = rng.choice(["log", "sqrt", "exp"])
        a = rng.uniform(1.0, 10.0)
        b = rng.uniform(0.05, 0.5)
        utilidades.append(Utilidad(tipo, a, b))
    return utilidades, B


# ---------------------------------------------------------------------------
# Parte 2: utilidad conjunta de COBERTURA PONDERADA.
# Hay un universo de M "tipos de datos" (0..M-1), cada uno con peso w_e > 0.
# El nodo i aporta datos de un subconjunto D_i del universo (de tamaño d).
# f(S) = suma de los pesos de los tipos cubiertos por al menos un nodo de S.
# ---------------------------------------------------------------------------
def instancia_cobertura(N, M, d, semilla=0):
    """N nodos, universo de M tipos, cada nodo cubre exactamente d tipos al azar."""
    rng = random.Random(semilla)
    pesos = [rng.uniform(1.0, 10.0) for _ in range(M)]
    conjuntos = [frozenset(rng.sample(range(M), d)) for _ in range(N)]
    return conjuntos, pesos
