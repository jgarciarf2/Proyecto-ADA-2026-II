"""
Datos de cada instancia, agrupados en dataclasses.

Los algoritmos reciben los campos sueltos (como en el pseudocódigo del documento);
estas clases sirven para generar, guardar y pasar instancias completas. Las variantes
agregan sus propios campos (costos, rondas, grafo) en clases nuevas.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class InstanciaReparto:
    """Parte 1: N utilidades cóncavas crecientes y un presupuesto entero B."""
    utilidades: list
    B: int

    @property
    def N(self):
        return len(self.utilidades)


@dataclass(frozen=True)
class InstanciaCobertura:
    """
    Parte 2: el nodo i cubre el conjunto conjuntos[i] de tipos de datos
    (enteros 0..M-1) y el tipo e pesa pesos[e] > 0.
    """
    conjuntos: list
    pesos: list

    @property
    def N(self):
        return len(self.conjuntos)

    @property
    def M(self):
        return len(self.pesos)
