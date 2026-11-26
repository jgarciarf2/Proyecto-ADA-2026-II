# Guía corta para la sustentación

Material de repaso para defender el problema, los algoritmos, sus garantías y las decisiones de implementación. Las secciones entre corchetes en el plan final deben asignarse entre los integrantes antes del ensayo.

## 1. Explicación del problema en un minuto

En cada una de T rondas elegimos hasta k nodos para maximizar una utilidad de influencia submodular. Después repartimos B unidades enteras de ruido entre los elegidos para maximizar una suma de utilidades cóncavas. Cada nodo también tiene un costo de participación y un saldo total de ruido Rᵢ que se acumula entre rondas. La selección y el reparto son problemas distintos: primero fijamos Sₜ; después optimizamos xₜ para ese grupo.

En la variante V2 algunos nodos fallan temporalmente al comienzo de cada ronda. Se observan antes de elegir, no gastan saldo al fallar y pueden volver en la ronda siguiente. La implementación usa fallas Bernoulli independientes, probabilidad común p y semilla reproducible.

## 2. Parte 1: por qué el voraz de reparto es óptimo

Para cada nodo i, la utilidad uᵢ es cóncava y sus ganancias marginales gᵢ(t) = uᵢ(t) − uᵢ(t−1) no aumentan con t. El algoritmo con montículo compara la siguiente unidad disponible de cada nodo y entrega la de mayor ganancia marginal.

**Argumento de intercambio.** Si una solución no eligió una unidad con ganancia más alta que una unidad que sí eligió, se intercambian: la utilidad total no disminuye. Al repetir el intercambio quedan elegidas las B ganancias marginales más altas. Por concavidad, si se elige la unidad t de un nodo, también conviene elegir sus unidades anteriores, así que el conjunto de unidades elegido siempre forma prefijos factibles por nodo. El resultado es óptimo para el presupuesto B y los topes de saldo.

**Tiempo.** Crear el montículo cuesta O(n); entregar B unidades cuesta O(B log n). Total O(n + B log n), espacio adicional O(n). El verificador por programación dinámica `exacto_dp` cuesta O(nB²) y se usa solo como referencia en instancias pequeñas; no es el algoritmo de entrega.

**Pseudo-polinomial.** El tiempo del voraz depende del valor numérico B. Si B se codifica en binario con β bits, B puede ser del orden de 2ᵝ; por eso esta implementación se llama pseudo-polinomial respecto de la longitud de B. Esto no dice que el voraz sea inexacto: su resultado sí es óptimo. La clasificación del problema y algoritmos alternativos se discuten en `docs/formulacion.md` §7.2.

## 3. Parte 2: NP-dureza por Cobertura Máxima

**Problema de decisión de origen.** COBERTURA-MÁXIMA recibe un universo U, conjuntos S₁,…,Sₘ, un cupo k y un umbral t. Pregunta si k conjuntos pueden cubrir al menos t elementos. Es NP-completo.

**Construcción.** Por cada conjunto Sᵢ se crea un nodo i; cada elemento de U se vuelve un elemento de cobertura con peso 1; se conserva k y se fija el mismo umbral t. La utilidad de cualquier grupo A queda f(A)=|∪ᵢ∈A Sᵢ|. La transformación se construye en O(|U| + Σᵢ|Sᵢ|), así que es polinomial.

**Dos direcciones.**

- Si k conjuntos cubren al menos t elementos, sus k nodos forman una solución de selección con f(A)≥t.
- Si existe un grupo A con |A|≤k y f(A)≥t, los conjuntos correspondientes cubren t elementos. Si el enunciado de origen pide exactamente k, se completa con conjuntos arbitrarios; por monotonía la cobertura no disminuye.

Así COBERTURA-MÁXIMA ≤ₚ SELECCIÓN. Si resolviéramos selección exactamente en tiempo polinomial, podríamos resolver Cobertura Máxima en tiempo polinomial; por eso selección es NP-difícil. La versión de decisión está en NP porque el grupo S sirve como certificado y su factibilidad y valor se verifican en tiempo polinomial.

**Dirección que hay que recordar:** desde el problema conocido como difícil hacia el problema del proyecto. Reducir nuestro problema a Cobertura Máxima no probaría que nuestro problema sea difícil.

La reducción desde Conjunto Dominante para la utilidad de influencia está en `docs/formulacion.md` §7.5; con pesos 0/1, f(S) cuenta los vértices dominados.

## 4. Parte 2: exacto y aproximado

**Referencia exacta.** La fuerza bruta recorre todos los grupos de tamaño hasta k cuando hay costos: O(Σⱼ≤ₖ C(N,j) · τ_f), donde τ_f es el costo de evaluar f. Para influencia densa, τ_f=O(Nk). En el caso sin costos se basta con grupos de tamaño k por monotonía. Con k cercano a N/2 hay exponencialmente muchos grupos; sirve como juez para casos pequeños.

**Voraz.** En cada paso calcula la ganancia marginal de cada candidato factible y agrega la más alta. Una ganancia de influencia cuesta O(N); hay a lo sumo Nk evaluaciones, así que T=O(N²k) con matriz densa. El espacio adicional es O(N).

**Idea de la cota (1−1/e).** Si f es monótona, submodular y f(∅)=0, sea Sₜ el grupo voraz y O un óptimo. La utilidad que falta δₜ=f(O)−f(Sₜ) está acotada por la suma de las ganancias de los elementos de O respecto a Sₜ. Hay a lo sumo k de esos elementos; el voraz elige una ganancia no menor que cada una. Por tanto δₜ₊₁≤(1−1/k)δₜ. Tras k pasos queda como máximo (1−1/k)ᵏ≤1/e de la brecha inicial, y f(Sₖ)≥(1−1/e)f(O)≈0,632f(O).

**Límite de la garantía.** Esa demostración requiere solo la restricción de cardinalidad. Con un presupuesto de costos, una elección puede gastar mucho presupuesto y la comparación de ganancias deja de servir. V1 tiene algoritmos A y B con garantías específicas por régimen. En V2, 1/k se garantiza respecto del óptimo factible del estado de una ronda ya observado si los costos pueden restringir; no se afirma una garantía contra la política dinámica óptima de T rondas.

## 5. Complejidades que conviene decir sin leer

| Algoritmo | Tiempo | Observación |
|---|---:|---|
| Reparto voraz con montículo | O(n + B log n) | Óptimo por concavidad; depende del valor de B |
| DP exacta de reparto | O(nB²) | Referencia de pruebas, seudopolinomial |
| Selección exacta por fuerza bruta | O(Σⱼ≤ₖ C(N,j)·τ_f) | Exponencial; referencia en casos pequeños |
| Selección voraz por influencia | O(N²k) | Una evaluación de ganancia cuesta O(N) |
| V1 algoritmo A | O(N²k) | Más rápido; garantía depende de si restringe el cupo |
| V1 algoritmo B | O(N⁵k) | Enumeración parcial; solo tamaños pequeños |
| V2 por T rondas | O(T(N²k + B log(k+1))) | Fallas, selección y reparto por ronda |

Para el reparto, el tamaño n de la tabla es el número de nodos elegidos en esa ronda y n≤k.

## 6. Dónde está cada cosa y cómo se mide

- Reparto: `ada/parte1/voraz.py`; casos exactos de referencia: `ada/parte1/dp.py`.
- Selección y fuerza bruta: `ada/parte2/`; caso de red por rondas: `ada/solucion_red.py`.
- V1: `ada/variantes/costos.py`; V2: `ada/variantes/rondas.py`.
- Experimentos: `experimentos/`; evidencia por caso: `experimentos/casos.py` y `resultados/casos/`.
- En los casos V2, `time.perf_counter` incluye generación de fallas, selección y reparto; excluye el óptimo opcional, las verificaciones y la escritura. `resultado.json` expresa segundos y `resumen.csv` milisegundos.
- La ejecución de la interfaz es `streamlit run app/principal.py`; el Modo demo permite ver selección paso a paso, reparto y V2.

## 7. Preguntas de práctica

1. ¿Por qué el reparto voraz es óptimo cuando las utilidades son cóncavas? Responde con ganancias marginales e intercambio.
2. ¿Qué significa pseudo-polinomial y por qué el algoritmo sigue siendo exacto?
3. ¿Por qué la reducción debe ir de Cobertura Máxima al problema de selección?
4. ¿Qué representa una solución en cada dirección de la reducción?
5. ¿Dónde se usa la submodularidad en la prueba de 1−1/e?
6. ¿Por qué no se aplica esa cota al voraz con costos?
7. ¿Qué mide τ_f y por qué una evaluación de influencia cuesta O(N)?
8. ¿Qué información conoce V2 al comenzar cada ronda y qué garantía no se afirma?
9. ¿Qué parte del tiempo medido incluye el cronómetro y qué deja por fuera?
10. ¿Qué casos comprueban p=0, probabilidad alta y todos caídos en una ronda?

## 8. Plan de repaso entre integrantes

Antes del ensayo, asignen una persona a cada bloque. Cada integrante debe explicar sin notas la reducción y la deducción de complejidad del algoritmo exacto; luego quien escucha plantea dos preguntas de la sección 7 y señala el paso que necesite más claridad.

| Bloque para repartir | Integrante | Tiempo de práctica |
|---|---|---:|
| Parte 1: intercambio, algoritmo y pseudo-polinomial | Por asignar | 5 min |
| Reducción: construcción y dos direcciones | Por asignar | 5 min |
| Parte 2: fuerza bruta, voraz y 1−1/e | Por asignar | 5 min |
| Variantes, código, experimentos y demo | Por asignar | 5 min |

El equipo debe completar los nombres, hacer el repaso cruzado y el ensayo cronometrado; esta guía no sustituye la práctica en el tablero.
