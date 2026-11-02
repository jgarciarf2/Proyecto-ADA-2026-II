"""
Parte 2 — Selección de nodos participantes.

Entrada: N nodos; el nodo i cubre el conjunto D_i de "tipos de datos";
         cada tipo e tiene peso w_e; un cupo k.
Utilidad conjunta (cobertura ponderada): f(S) = sum_{e in U_{i in S} D_i} w_e
Objetivo: elegir S con |S| <= k que maximice f(S).

  cobertura.f, cobertura.ganancia_marginal  -> la utilidad (tau = O(d))
  voraz.voraz_submodular                    -> aproximación (1 - 1/e), O(N k d)
  fuerza_bruta.fuerza_bruta                 -> óptimo exacto, O(C(N,k) k d)
  reduccion.reducir_desde_cobertura_maxima  -> la reducción de NP-dureza
"""
from ada.parte2.cobertura import f, ganancia_marginal
from ada.parte2.fuerza_bruta import fuerza_bruta
from ada.parte2.reduccion import reducir_desde_cobertura_maxima
from ada.parte2.voraz import voraz_submodular
