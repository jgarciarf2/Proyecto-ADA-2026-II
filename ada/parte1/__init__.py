"""
Parte 1 — Reparto óptimo del presupuesto.

Entrada: N utilidades cóncavas crecientes u_1..u_N y un presupuesto entero B.
Salida:  x_1..x_N enteros >= 0 con sum x_i <= B que maximiza sum u_i(x_i).

  voraz.voraz_heap  -> el algoritmo del proyecto, O(N + B log N)
  dp.exacto_dp      -> verificador independiente, O(N * B^2), solo para instancias pequeñas
"""
from ada.parte1.dp import exacto_dp
from ada.parte1.voraz import ContadorComparaciones, voraz_heap
