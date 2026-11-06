# Proyecto ADA 2026-2: Reparto de presupuesto y selección de participantes

Proyecto semestral de Análisis y Diseño de Algoritmos. Una red de N nodos entrena un modelo en T rondas. En cada ronda hay que decidir **qué nodos participan** (Parte 2) y **cuánto presupuesto de ruido se le da a cada uno** (Parte 1).

| Parte | Problema | Técnica | Dificultad |
|---|---|---|---|
| 1. Reparto del presupuesto | Repartir B unidades entre N nodos con utilidades cóncavas | Voraz con montículo, óptimo por intercambio | Polinomial: `O(N + B log N)` |
| 2. Selección de participantes | Elegir k de N nodos que maximicen una utilidad submodular | Voraz submodular, cota `(1 − 1/e)` | NP-difícil (reducción desde Cobertura Máxima) |
| Variantes (todas obligatorias) | Costos de participación · T rondas con fallas · nodos vecinos | V1 y T rondas (sin fallas) ya están en la solución base; el resto es de la entrega final | Por definir |

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
| 1-2 | Equipo, variante y formalización escrita (sin código) | ✅ Primera entrega: `docs/formulacion.md` y `docs/manual_tecnico.md` (Word/PDF en `entregables/`) · ⬜ formalizar V2 con fallas y V3 |
| 3-4 | Prueba de NP-dureza (revisa la profesora) | ✅ Hecha: `docs/formulacion.md` §7 (desde Cobertura Máxima y desde Conjunto Dominante) |
| 5-6 | Algoritmo exacto y su T(n) | ✅ Parte 1 (voraz + verificador DP); ✅ Parte 2 (fuerza bruta) |
| 7-8 | Aproximado, su T(n) y su cota | ✅ Voraz submodular con `(1 − 1/e)` |
| 9-10 | Experimentos | ✅ Parte 1 y Parte 2 · ⬜ variantes |
| 11 | Entrega final y sustentación | ⬜ |

**Resumen:** la primera entrega está completa: formulación con las dos reducciones, solución base para los casos de la profesora (T rondas, k y costos ≤ P, tope por nodo), 10 casos propios, 35 pruebas y manual técnico. Para la entrega final faltan **las variantes** (fallas en V2, vecinos en V3 y un voraz con garantía para V1) y el **informe final**.

---

## 3. Arquitectura

El código está separado en tres capas: **lógica** (`ada/`), **medición** (`experimentos/`) y **correctitud** (`tests/`). Cada archivo tiene una sola responsabilidad y menos de ~150 líneas, para que se pueda explicar en la sustentación.

```
Proyecto-ADA-2026-II/
├── README.md                     ← este archivo: mapa del proyecto
├── requirements.txt              ← numpy, matplotlib, pytest
├── pytest.ini                    ← configuración de las pruebas
│
├── ada/                          ← TODA la lógica (no dibuja ni escribe archivos)
│   ├── modelo.py                 ← dataclasses: InstanciaReparto, InstanciaCobertura, InstanciaInfluencia
│   ├── utilidades.py             ← utilidades cóncavas: UtilidadLog, UtilidadRaiz, UtilidadSaturacion, UtilidadTabla, UtilidadConTope
│   ├── generadores.py            ← todas las instancias sintéticas (semilla fija)
│   ├── parte1/
│   │   ├── voraz.py              ← voraz con heap O(N + B log N) + ContadorComparaciones
│   │   └── dp.py                 ← verificador exacto O(N·B²)
│   ├── parte2/
│   │   ├── cobertura.py          ← f(S) y ganancia marginal
│   │   ├── voraz.py              ← voraz submodular O(N·k·d), cota (1 − 1/e)
│   │   ├── fuerza_bruta.py       ← óptimo exacto O(C(N,k)·k·d)
│   │   ├── reduccion.py          ← reducción desde Cobertura Máxima
│   │   └── influencia.py         ← utilidad de influencia sobre el grafo (formato de la profesora)
│   ├── casos.py                  ← formato JSON provisional: leer y validar, óptimo de referencia, resultado serializable
│   ├── casos_red.py              ← lector del formato de la profesora (parametros, grafo, nodos)
│   ├── solucion_red.py           ← solución base para ese formato: T rondas, k y costo ≤ P, tope por nodo
│   ├── ronda.py                  ← solución base: selecciona k nodos y reparte B entre ellos, con trazas
│   ├── verificacion.py           ← revisa |S| ≤ k, Σxᵢ ≤ B, xᵢ entero ≥ 0 y los valores recalculados
│   └── variantes/                ← V1 costos.py · V2 rondas.py · V3 vecinos.py (por crear)
│
├── experimentos/                 ← miden, guardan CSV y grafican contra la teoría
│   ├── comun.py                  ← medir (mediana), guardar CSV, gráfica medido/teoría/cociente
│   ├── casos.py                  ← ejecuta casos .json y guarda la evidencia (resultado, tiempo, trazas)
│   ├── parte1.py
│   ├── parte2.py
│   ├── influencia.py             ← voraz de influencia: tiempo contra c·N²·k y cota (1 − 1/e) en 300 instancias
│   ├── figuras_informe.py        ← figuras del documento de formulación
│   └── figuras_manual.py         ← diagramas UML del manual técnico
│
├── app/                          ← interfaz en Streamlit (solo muestra; no tiene lógica)
│   ├── principal.py              ← punto de entrada y navegación
│   ├── paginas.py                ← Cargar caso · Evidencias · Modo demo · Experimentos
│   ├── vista_resultado.py        ← métricas, pestañas y verificación de un caso
│   ├── vista_red.py              ← vista de los casos de la profesora (rondas, influencia, presupuesto por nodo)
│   ├── graficas.py               ← selección paso a paso, mapa de cobertura, nivel de agua del reparto
│   └── estilos.py                ← colores, íconos SVG y CSS
│
├── casos/profesora/              ← casos entregados por la profesora
├── casos/propios/                ← 10 casos propios en el formato de la profesora (situaciones límite)
├── casos/ejemplos/               ← casos de ejemplo en el formato JSON provisional
│
├── tests/                        ← correctitud en menos de 1 s
│   ├── test_parte1.py            ← voraz == DP (300 casos), presupuesto, conteo, contraejemplo sin concavidad
│   ├── test_parte2.py            ← monotonía/submodularidad, cota (1 − 1/e), E(N,k), ejemplo de la reducción
│   ├── test_ronda.py             ← trazas, verificación de restricciones y solución base
│   ├── test_casos.py             ← formato de casos (válidos e inválidos) y ejecución de un caso
│   └── test_red.py               ← influencia submodular, voraz con costos, caso de la profesora
│
├── resultados/{parte1,parte2,influencia,casos}/   ← CSV, gráficas y evidencia de cada caso
├── docs/                         ← documentación técnica en Markdown
│   ├── 01_formalizacion_y_parte1.md, 02_parte2.md  ← notas teóricas iniciales de las Partes 1 y 2
│   ├── formulacion.md            ← formulación completa de la primera entrega (modelo, demostraciones, reducciones, T(n))
│   ├── manual_tecnico.md         ← manual técnico: arquitectura, UML, formatos, ejecución, pruebas, limitaciones
│   ├── figuras/                  ← diagramas del documento (python -m experimentos.figuras_informe)
│   └── entrega-1/                ← PDF entregados: informe (formulación) y manual técnico
└── entregables/                  ← informe, manual y evidencias en PDF/Word (NO se sube al repo)
```

**Solución base de una ronda** (`ada/ronda.py`): `resolver_ronda(conjuntos, pesos, k, utilidades, B)` elige S con el voraz submodular, reparte B entre los nodos de S con el voraz de heap y verifica las restricciones. Devuelve la selección, el reparto, las trazas de los dos voraces (nodo elegido y ganancia marginal en cada paso), un resumen del reparto por nodo y el tiempo de cada parte. Costo: `T = O(N·k·d + B log k)`.

**Reglas para mantenerlo ordenado:**
- `ada/` solo calcula: no imprime, no grafica, no escribe archivos. `experimentos/` mide y grafica.
- Los algoritmos reciben los datos sueltos, como en el pseudocódigo del documento (`voraz_heap(utilidades, B)`). Las dataclasses de `modelo.py` sirven para generar y pasar instancias completas.
- Hay **una sola versión** de cada algoritmo. Para contar operaciones o registrar la traza se le pasa un parámetro opcional (`contador=`, `traza=[]`) en vez de copiar el algoritmo. Sin esos parámetros, el algoritmo hace exactamente lo mismo.
- Las instancias salen siempre de `generadores.py` con semilla fija, para poder reproducir los resultados.
- Una utilidad nueva es una clase que hereda de `Utilidad` e implementa `__call__`.
- Toda función nueva de `ada/` lleva su prueba en `tests/` y su costo en el docstring.
- Commits pequeños y en español, uno por cosa.

### Cómo agregar una variante (ejemplo V1)
1. `ada/variantes/costos.py`: el algoritmo, con su T(n) en el docstring.
2. Si necesita datos nuevos, una dataclass en `modelo.py` y su generador en `generadores.py`.
3. `tests/test_variantes.py`: comparar contra fuerza bruta en instancias pequeñas.
4. `experimentos/variantes.py`: tiempos con al menos 5 tamaños de n, usando `experimentos/comun.py`.
5. `docs/03_variantes.md`: formalización, cota y resultados.

---

## 4. Lo que falta y propuesta de reparto

| # | Tarea | Para cuándo | Responsable |
|---|---|---|---|
| 1 | ~~Documento de la primera entrega~~ ✅ `docs/formulacion.md` + manual técnico | Primera entrega | |
| 2 | Variante 1 (costos): formalizar, implementar y citar la cota de Khuller, Moss y Naor (1999) | | |
| 3 | Variante 2 (T rondas con fallas): formalizar el modelo de fallas y el presupuesto acumulado | | |
| 4 | Variante 3 (vecinos): formalizar el efecto de los vecinos y ver si se conserva la concavidad | | |
| 5 | ~~Reorganizar carpetas según la §3~~ ✅ hecho | — | |
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
4. Los casos traen un grafo con pesos de influencia pero no la fórmula de f ni de uᵢ. ¿Son correctas las que supusimos (ver §6, "Casos de la profesora")?
5. V3: ¿cómo afecta el gasto a los vecinos (aditivo, puede ser negativo)? ¿Debe conservarse la concavidad?
6. V2: ¿el presupuesto de ruido es por nodo y se acumula en las T rondas? ¿Las fallas son aleatorias, y se conocen antes o después de seleccionar?
7. ¿Hay plantilla para el informe final? (La guía de la primera entrega ya respondió el formato: informe, repositorio y manual técnico.)

---

## 6. Cómo ejecutar

Requisitos: Python 3.10+. Todo se corre **desde la raíz del proyecto**.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt

python -m pytest                  # correctitud, menos de 1 s
python -m experimentos.parte1     # ~2 min: tiempos, ajuste c1·N + c2·B·log N, conteo de comparaciones
python -m experimentos.parte2     # ~20 s: cota (1−1/e), tiempos del voraz, voraz vs. fuerza bruta
python -m experimentos.influencia # ~1 min: voraz de influencia contra c·N²·k y cota con y sin costos
```

Los CSV y las gráficas quedan en `resultados/parte1/`, `resultados/parte2/` y `resultados/influencia/`.

### Ejecutar casos (evidencia de la entrega)

```bash
python -m experimentos.casos                    # los casos de casos/ejemplos/
python -m experimentos.casos casos/profesora/   # los casos de la profesora
python -m experimentos.casos casos/propios/     # los 10 casos propios (situaciones límite)
```

**Casos de la profesora.** Traen N, T rondas, k, B y un presupuesto de participación P por ronda; un grafo con pesos de influencia; y por nodo un coeficiente de utilidad, un costo y un presupuesto total. Mientras la profesora no confirme las fórmulas, usamos estos **supuestos**: uᵢ(x) = aᵢ·ln(1 + x); f(S) = Σᵥ aᵥ·(1 − Πᵤ∈S (1 − wᵤᵥ)) con wᵥᵥ = 1 (influencia probabilística, monótona y submodular); grafo no dirigido; en cada ronda se exige |S| ≤ k y Σ cᵢ ≤ P a la vez, y ningún nodo pasa su presupuesto total. Están en [ada/casos_red.py](ada/casos_red.py) y [ada/solucion_red.py](ada/solucion_red.py).

Por cada caso se crea `resultados/casos/<nombre>/` con `resultado.json` (entrada, selección, reparto, tiempos, trazas y verificación), `traza_seleccion.csv`, `traza_reparto.csv` y `reparto.csv`. En los casos de la profesora también se crea `verificacion.csv`. Además se genera `resultados/casos/resumen.csv` con una fila por caso. El programa reconoce dos formatos: el de la profesora ([ada/casos_red.py](ada/casos_red.py)) y el provisional que usamos antes de recibirlo ([ada/casos.py](ada/casos.py), solo para `casos/ejemplos/`). Los dos están descritos en `docs/manual_tecnico.md` §8.

### Interfaz visual

```bash
pip install -r requirements-app.txt
streamlit run app/principal.py
```

Tiene cuatro secciones. **Cargar caso** resuelve un JSON subido o de ejemplo. **Evidencias** muestra los casos guardados en `resultados/casos/`. **Modo demo** tiene controles para N, k y B, pensados para la sustentación. **Experimentos** reúne las gráficas de tiempo contra la teoría. La interfaz solo presenta resultados: la evidencia oficial son los archivos que genera `experimentos.casos`.

