# Proyecto ADA 2026-2: Reparto de presupuesto y selección de participantes

Proyecto semestral de Análisis y Diseño de Algoritmos. Una red de N nodos entrena un modelo en T rondas. En cada ronda hay que decidir **qué nodos participan** (Parte 2) y **cuánto presupuesto de ruido se le da a cada uno** (Parte 1).

| Parte | Problema | Técnica | Dificultad |
|---|---|---|---|
| 1. Reparto del presupuesto | Repartir B unidades entre N nodos con utilidades cóncavas | Voraz con montículo, óptimo por intercambio | Polinomial: `O(N + B log N)` |
| 2. Selección de participantes | Elegir k de N nodos que maximicen una utilidad submodular | Voraz submodular, cota `(1 − 1/e)` | NP-difícil (reducción desde Cobertura Máxima) |
| Variantes (todas obligatorias) | Costos de participación · T rondas con fallas · nodos vecinos | Por definir | Por definir |

---

## 1. Qué se nos evalúa

| Componente | Peso |
|---|---|
| Formalización (n, entrada, salida, objetivo) | 10 % |
| Prueba de NP-dureza por reducción | 10 % |
| T(n) del algoritmo exacto, deducida paso a paso | 10 % |
| Algoritmo aproximado: diseño, T(n) y cota | 15 % |
| Validación experimental (tiempo medido vs. teoría, mínimo 5 tamaños de n) | 10 % |
| **Sustentación** (grupal sin notas + individual) | **45 %** |

En la sustentación grupal cada uno debe poder explicar **sin notas** la reducción de NP-dureza y la deducción de T(n) del exacto.

---

## 2. Estado frente al cronograma

| Semanas | Hito | Estado |
|---|---|---|
| 1-2 | Equipo, variante y formalización escrita (sin código) | 🟡 Parte 1 y Parte 2 formalizadas; **faltan las variantes y el documento de entrega** |
| 3-4 | Prueba de NP-dureza (revisa la profesora) | ✅ Hecha: `docs/02_parte2.md` §3 |
| 5-6 | Algoritmo exacto y su T(n) | ✅ Parte 1 (voraz + verificador DP); ✅ Parte 2 (fuerza bruta) |
| 7-8 | Aproximado, su T(n) y su cota | ✅ Voraz submodular con `(1 − 1/e)` |
| 9-10 | Experimentos | ✅ Parte 1 y Parte 2 · ⬜ variantes |
| 11 | Entrega final y sustentación | ⬜ |

**Resumen:** el núcleo (Partes 1 y 2) está completo con teoría, código y gráficas. Lo que falta son **las tres variantes**, el **documento formal de la primera entrega** y el **informe final**.

---

## 3. Arquitectura propuesta

Hoy todo el código está en la raíz. Proponemos ordenarlo así antes de empezar las variantes, para que cada quien trabaje en su carpeta sin pisarse:

```
Proyecto-ADA-2026-II/
├── README.md                  ← este archivo: mapa del proyecto
├── requirements.txt           ← numpy, matplotlib
│
├── src/                       ← algoritmos (solo lógica, sin gráficas)
│   ├── instancias.py          ← generadores sintéticos con semilla fija
│   ├── parte1_reparto.py      ← voraz con heap + verificador DP
│   ├── parte2_seleccion.py    ← cobertura, voraz submodular, fuerza bruta, reducción
│   └── variantes/
│       ├── v1_costos.py       ← selección con costos (budgeted max coverage)
│       ├── v2_rondas.py       ← T rondas con nodos que fallan
│       └── v3_vecinos.py      ← nodos en grafo, el gasto afecta a los vecinos
│
├── experimentos/              ← un script por parte; cada uno genera CSV y PNG
│   ├── exp_parte1.py
│   ├── exp_parte2.py
│   └── exp_variantes.py
│
├── tests/                     ← pruebas rápidas de correctitud (voraz vs. exacto)
│
├── resultados/                ← salida de los experimentos (CSV + gráficas)
│   ├── parte1/  parte2/  variantes/
│
└── docs/                      ← lo que se entrega
    ├── 00_formalizacion.md    ← primera entrega (n, entrada, salida, objetivo)
    ├── 01_formalizacion_y_parte1.md   (ya existe)
    ├── 02_parte2.md                   (ya existe)
    ├── 03_variantes.md        ← nuevo
    └── informe/               ← informe técnico final
```

**Reglas para mantenerlo ordenado:**
- `src/` no dibuja ni escribe archivos; solo calcula. `experimentos/` mide y grafica.
- Cada algoritmo trae su función contadora de operaciones (como `voraz_heap_contando`), porque la teoría se valida con conteos y no solo con tiempos.
- Instancias siempre con semilla fija, para que los resultados se puedan reproducir.
- Cada resultado en `docs/` cita el CSV o la gráfica de `resultados/` que lo respalda.
- Commits pequeños y en español, uno por cosa.

---

## 4. Lo que falta y propuesta de reparto

| # | Tarea | Para cuándo | Responsable |
|---|---|---|---|
| 1 | `docs/00_formalizacion.md`: formalización de las Partes 1 y 2 **y de las 3 variantes**, con los nombres del equipo | Primera entrega | |
| 2 | Variante 1 (costos): formalizar, implementar y citar la cota de Khuller, Moss y Naor (1999) | | |
| 3 | Variante 2 (T rondas con fallas): formalizar el modelo de fallas y el presupuesto acumulado | | |
| 4 | Variante 3 (vecinos): formalizar el efecto de los vecinos y ver si se conserva la concavidad | | |
| 5 | Reorganizar carpetas según la §3 | Antes de las variantes | |
| 6 | Experimentos de las variantes (mínimo 5 tamaños de n) | Semanas 9-10 | |
| 7 | Informe técnico final | Semana 11 | Todos |
| 8 | Ensayar la sustentación: reducción y T(n) sin notas | Semana 11 | Todos |

### Ideas iniciales para las variantes
- **V1 Costos:** cada nodo tiene un costo `c_i` y se exige `Σ c_i ≤ P` en lugar de `|S| ≤ k`. El voraz por razón ganancia/costo, solo, puede ser muy malo. Hay dos versiones conocidas: tomar el mejor entre ese voraz y el mejor nodo individual da `(1 − 1/e)/2`, y enumerar parcialmente todos los conjuntos de 3 nodos y completar con el voraz da `(1 − 1/e)`.
- **V2 Rondas:** repetir la selección T veces. Antes de cada ronda una fracción de nodos falla y no está disponible, y el presupuesto de ruido de cada nodo se descuenta ronda a ronda.
- **V3 Vecinos:** grafo `G = (V, E)`. Por ejemplo, `u_i(x_i + α · Σ_{j ∈ vecinos(i)} x_j)`. Si el efecto ya no es separable, el voraz de la Parte 1 puede dejar de ser óptimo, y eso hay que demostrarlo o mostrarlo con un contraejemplo.

---

## 5. Preguntas para la profesora

1. El cronograma habla de "elección de la variante" en las semanas 1-2, pero el §4.4 dice que las variantes son "todas obligatorias". ¿Hacemos las tres? ¿En la primera entrega se formalizan todas?
2. En la Parte 1 el enunciado toma n = N, pero el tiempo depende del **valor** de B (es pseudo-polinomial). ¿Acepta que el tamaño de entrada sea (N, B)?
3. Como algoritmo exacto de la Parte 2, ¿basta la fuerza bruta `O(C(N,k) · k · d)`?
4. ¿Podemos usar cobertura ponderada como utilidad submodular concreta, o quiere f como un oráculo general? Con cobertura, T pasa de `O(N·k)` a `O(N·k·d)`.
5. V3: ¿cómo afecta el gasto a los vecinos (aditivo, puede ser negativo)? ¿Debe conservarse la concavidad?
6. V2: ¿el presupuesto de ruido es por nodo y se acumula en las T rondas? ¿Las fallas son aleatorias, y se conocen antes o después de seleccionar?
7. ¿En qué formato se entrega (PDF, Word, repositorio)? ¿Hay plantilla para el informe?

---

## 6. Cómo ejecutar (estructura actual)

Requisitos: Python 3.10+ con `pip install numpy matplotlib`.

```bash
python experimentos_parte1.py   # ~2 min: correctitud, tiempos, conteo de operaciones
python experimentos_parte2.py   # ~20 s: submodularidad, cota (1−1/e), voraz vs. fuerza bruta
```

Los CSV y las gráficas quedan en `resultados/`.

| Archivo actual | Qué es |
|---|---|
| `instancias.py` | Generador de instancias sintéticas |
| `parte1_reparto.py` | Voraz con heap `O(N + B log N)` y verificador exacto DP |
| `parte2_seleccion.py` | Utilidad de cobertura, voraz `O(N·k·d)`, fuerza bruta, reducción desde Cobertura Máxima |
| `experimentos_parte1.py` / `experimentos_parte2.py` | Experimentos y gráficas |
| `docs/01_formalizacion_y_parte1.md` | Formalización y demostración de la Parte 1 |
| `docs/02_parte2.md` | Reducción NP, T(N,k), cota `(1 − 1/e)` y resultados de la Parte 2 |
