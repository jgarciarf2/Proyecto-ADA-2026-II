"""
Paquete del proyecto ADA 2026-2: reparto de presupuesto y selección de participantes.

Toda la lógica vive aquí y no dibuja ni escribe archivos:
  modelo       -> dataclasses con los datos de cada instancia
  utilidades   -> funciones cóncavas y crecientes de la Parte 1
  generadores  -> instancias sintéticas reproducibles (semilla fija)
  parte1       -> reparto óptimo del presupuesto (voraz + verificador DP)
  parte2       -> selección de participantes (cobertura, voraz, fuerza bruta, reducción)
  variantes    -> costos de participación, T rondas con fallas, nodos vecinos
"""
