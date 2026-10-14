# Proyecto ADA 2026-2 — Subproyecto 2 (Presupuesto y participantes)

Requisitos: Python 3.10+, numpy, matplotlib  (`pip install numpy matplotlib`)

| Archivo | Qué es |
|---|---|
| `instancias.py` | Generador de instancias sintéticas (semilla fija) |
| `parte1_reparto.py` | Parte 1: voraz con montículo O(N + B log N) + verificador exacto DP |
| `experimentos_parte1.py` | Correctitud, tiempos, conteo de operaciones y gráficas |
| `parte2_seleccion.py` | Parte 2: utilidad de cobertura, voraz submodular O(N·k·d), fuerza bruta, reducción desde Cobertura Máxima |
| `experimentos_parte2.py` | Sanidad submodular, cota (1−1/e), tiempos, voraz vs. fuerza bruta |
| `docs/01_formalizacion_y_parte1.md` | Formalización (ambas partes) + demostración y análisis de la Parte 1 |
| `docs/02_parte2.md` | Parte 2: reducción NP-dureza, T(N,k), cota (1−1/e) con idea de prueba, resultados |
| `resultados/` | CSV y gráficas generadas |

Ejecutar:  `python experimentos_parte1.py`  (~2 min)  y  `python experimentos_parte2.py`  (~20 s)

Pendiente: variantes (costos/Khuller, T rondas con fallas, nodos en grafo), informe, sustentación.
