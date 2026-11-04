"""
Utilidades de la Parte 1: funciones u(x) sobre enteros x >= 0, crecientes y
cóncavas, con u(0) = 0. Tres familias clásicas:

    log:   u(x) = a * ln(1 + x)
    sqrt:  u(x) = a * sqrt(x)
    exp:   u(x) = a * (1 - e^{-b x})      (saturación)

En las tres, la ganancia marginal g(x) = u(x+1) - u(x) es positiva y no
creciente en x, que es exactamente la definición de cóncava en enteros.
Evaluar cualquiera cuesta O(1).

Para una familia nueva (por ejemplo, la variante de vecinos) basta con
heredar de Utilidad e implementar __call__.
"""
import math


class Utilidad:
    """Base: una utilidad se evalúa con u(x) y da su ganancia marginal."""

    __slots__ = ()

    def __call__(self, x):
        raise NotImplementedError

    def marginal(self, x):
        """Ganancia de dar la unidad número x+1: u(x+1) - u(x)."""
        return self(x + 1) - self(x)


class UtilidadLog(Utilidad):
    __slots__ = ("a",)

    def __init__(self, a):
        self.a = a

    def __call__(self, x):
        return self.a * math.log1p(x)

    def __repr__(self):
        return f"UtilidadLog(a={self.a:.2f})"


class UtilidadRaiz(Utilidad):
    __slots__ = ("a",)

    def __init__(self, a):
        self.a = a

    def __call__(self, x):
        return self.a * math.sqrt(x)

    def __repr__(self):
        return f"UtilidadRaiz(a={self.a:.2f})"


class UtilidadTabla(Utilidad):
    """
    Utilidad dada como tabla de valores: u(x) = valores[x]. Después del último
    valor se queda constante (ganancia marginal 0). Sirve para casos que traen
    la utilidad punto a punto en vez de una fórmula.
    """
    __slots__ = ("valores",)

    def __init__(self, valores):
        self.valores = list(valores)

    def __call__(self, x):
        return self.valores[min(x, len(self.valores) - 1)]

    def __repr__(self):
        return f"UtilidadTabla({len(self.valores)} valores)"


class UtilidadConTope(Utilidad):
    """
    u(min(x, tope)): la misma utilidad, pero después de 'tope' unidades ya no gana nada.
    Sirve para el presupuesto que le queda a un nodo. Sigue siendo cóncava y creciente.
    """
    __slots__ = ("base", "tope")

    def __init__(self, base, tope):
        self.base, self.tope = base, tope

    def __call__(self, x):
        return self.base(min(x, self.tope))

    def __repr__(self):
        return f"UtilidadConTope({self.base!r}, tope={self.tope})"


class UtilidadSaturacion(Utilidad):
    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a, self.b = a, b

    def __call__(self, x):
        return self.a * (1.0 - math.exp(-self.b * x))

    def __repr__(self):
        return f"UtilidadSaturacion(a={self.a:.2f}, b={self.b:.2f})"
