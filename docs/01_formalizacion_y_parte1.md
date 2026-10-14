# Proyecto ADA 2026-2 — Subproyecto 2: Reparto de presupuesto y selección de participantes

## 1. Formalización del problema (entregable 1)

### 1.1 Parte 1 — Reparto óptimo del presupuesto

- **Tamaño de la entrada:** `N` (número de nodos ya seleccionados para la ronda) y `B` (presupuesto total, en unidades enteras).
  - *Justificación:* el algoritmo trabaja nodo por nodo (crece con `N`) y unidad por unidad (crece con el **valor** de `B`). Por eso las dos medidas son necesarias. Ojo: `B` cuenta como valor numérico, no como longitud en bits (ver §2.4).
- **Entrada:** para cada nodo `i ∈ {1..N}`, una función `u_i : ℤ≥0 → ℝ` con `u_i(0) = 0`, **creciente** y **cóncava**. En enteros, cóncava significa que la ganancia marginal `g_i(t) = u_i(t) − u_i(t−1)` es no creciente en `t`. Además se recibe el entero `B ≥ 0`. Evaluar cada `u_i` cuesta `O(1)`.
- **Salida:** un vector de enteros `x = (x_1, …, x_N)` con `x_i ≥ 0` y `Σ x_i ≤ B`.
- **Objetivo:** maximizar `U(x) = Σ_i u_i(x_i)`.

### 1.2 Parte 2 — Selección de nodos participantes

- **Tamaño de la entrada:** `N` (nodos candidatos) y `k` (cupo de la ronda, `k < N`). Además, `τ` = costo de evaluar la utilidad conjunta (o su ganancia marginal) una vez.
  - *Justificación:* el espacio de soluciones tiene `C(N, k)` subconjuntos, que crece con `N` y `k`. La función `f` se recibe como oráculo, así que su costo `τ` entra como parámetro aparte.
- **Entrada:** el conjunto de nodos `V = {1..N}`, el entero `k` y una función `f : 2^V → ℝ≥0` que es
  - **monótona:** `A ⊆ A' ⇒ f(A) ≤ f(A')`;
  - **submodular:** para `A ⊆ A'` y `v ∉ A'`, `f(A ∪ {v}) − f(A) ≥ f(A' ∪ {v}) − f(A')`.
- **Salida:** un subconjunto `S ⊆ V` con `|S| ≤ k`.
- **Objetivo:** maximizar `f(S)`.
- **Utilidad concreta que vamos a implementar (cobertura ponderada):** cada nodo `i` tiene datos de un subconjunto `D_i` de un universo de `M` "tipos de datos" (clases, regiones, perfiles de usuario), y cada tipo `e` tiene un peso `w_e > 0`. La utilidad es `f(S) = Σ_{e ∈ ∪_{i∈S} D_i} w_e`, es decir, cuánta diversidad de datos aportan en conjunto los participantes. Es monótona y submodular (se demuestra en la Parte 2), y además permite construir la reducción desde Cobertura Máxima de forma directa.

---

## 2. Parte 1 — Algoritmo voraz y su optimalidad

### 2.1 Algoritmo

```
VORAZ-REPARTO(u_1..u_N, B):
1  x_i ← 0 para todo i
2  H ← montículo de máximos con los pares (g_i(1), i)        // heapify
3  repetir B veces:
4      (g, i) ← máximo de H
5      x_i ← x_i + 1
6      reemplazar la raíz de H por (g_i(x_i + 1), i)           // heapreplace
7  devolver x
```

Supuesto: las `u_i` son **estrictamente** crecientes (`g_i(t) > 0`), como en nuestras instancias. Así el voraz gasta exactamente `B`. Si alguna ganancia puede ser 0, el código para cuando la mayor ganancia es 0; esas unidades no cambian la utilidad y el argumento no cambia.

### 2.2 Invariante clave

En todo momento, el par que guarda `H` para el nodo `i` es su **siguiente** unidad, `g_i(x_i + 1)`. Como `g_i` es no creciente, esa es la mejor unidad que le queda al nodo `i`. Por lo tanto, la raíz de `H` es la mayor ganancia marginal disponible entre todos los nodos.

### 2.3 Teorema (optimalidad). El voraz devuelve un reparto de utilidad máxima.

**Demostración (argumento de intercambio).** Sea `G = (G_1..G_N)` el reparto del voraz, con `Σ G_i = B`. Sea `O` un reparto óptimo que, entre todos los óptimos, minimiza la distancia `d(O, G) = Σ_i |O_i − G_i|`. Como las ganancias son positivas, podemos suponer `Σ O_i = B`: si sobrara presupuesto, agregar una unidad a cualquier nodo no empeora la solución.

Supongamos, para llegar a una contradicción, que `O ≠ G`. Como ambos suman `B`, existen nodos `i` y `j` con `O_i > G_i` y `O_j < G_j`.

Ahora movemos la **última** unidad de `i` en `O` hacia `j`, y formamos `O' = O − e_i + e_j`. El cambio en la utilidad es

  `Δ = g_j(O_j + 1) − g_i(O_i)`.

Veamos que `Δ ≥ 0` con esta cadena de desigualdades:

1. `g_j(O_j + 1) ≥ g_j(G_j)`, por concavidad de `u_j`, porque `O_j + 1 ≤ G_j`.
2. Consideremos el momento en que el voraz le dio a `j` su unidad número `G_j`. En ese momento `i` tenía `y ≤ G_i` unidades, así que su unidad disponible era `g_i(y + 1)`. El voraz escogió `j` porque era la raíz del heap (invariante 2.2). Entonces `g_j(G_j) ≥ g_i(y + 1)`.
3. `g_i(y + 1) ≥ g_i(G_i + 1) ≥ g_i(O_i)`, por concavidad de `u_i`, porque `y + 1 ≤ G_i + 1 ≤ O_i`.

Encadenando: `Δ = g_j(O_j + 1) − g_i(O_i) ≥ 0`. Entonces `U(O') ≥ U(O)`, así que `O'` también es óptimo. Pero `d(O', G) = d(O, G) − 2`, lo que contradice que `O` fuera el óptimo más cercano a `G`. Luego `O = G`, y el voraz es óptimo. ∎

> **Para la sustentación (la idea en una frase):** con concavidad, la utilidad de un reparto es la suma de las unidades que se toman de cada nodo, y de cada nodo siempre se toman las primeras (las mejores). El voraz se queda con las `B` mejores unidades de todas. Cualquier reparto distinto tiene alguna unidad peor que se puede cambiar por una mejor sin perder nada.

**¿Dónde se usa la concavidad?** En los pasos 1 y 3. Sin concavidad el voraz falla. Contraejemplo: `u_1(x) = x` y `u_2` con `u_2(1) = 0` y `u_2(2) = 10` (no cóncava), con `B = 2`. El voraz da las dos unidades al nodo 1 (utilidad 2), pero el óptimo es darlas al nodo 2 (utilidad 10).

### 2.4 Función de eficiencia (deducción contando operaciones)

| Línea | Operación | Costo |
|---|---|---|
| 1 | inicializar `x` | `N` asignaciones → `O(N)` |
| 2 | calcular `N` ganancias iniciales (`O(1)` cada una) + heapify | `N·O(1) + O(N)` (heapify hace a lo sumo `2N` comparaciones) |
| 4 | leer la raíz | `O(1)` |
| 5 | incremento | `O(1)` |
| 6 | evaluar 1 ganancia + `heapreplace` (hundir la raíz por un árbol de altura `⌊log₂ N⌋`, con a lo sumo 2 comparaciones por nivel) | `O(1) + O(log N)` |
| 3 | el ciclo se repite `B` veces | `B · O(log N)` |

```
T(N, B) = c₁·N + B·(c₂ + c₃·log₂ N) = O(N + B log N)
```

**Es pseudo-polinomial.** `B` se escribe con `⌈log₂ (B+1)⌉` bits. Si llamamos `β` a esa longitud, `B ≈ 2^β` y `T = O(N + 2^β log N)`, que es exponencial en el tamaño real de la entrada. Es el mismo fenómeno que en la DP de la mochila. Aquí no contradice ninguna dificultad: el problema sí admite algoritmos polinomiales de verdad (ver la observación siguiente).

**Presupuesto continuo (water-filling).** Si `x_i ∈ ℝ≥0` y las `u_i` son derivables y cóncavas, las condiciones de optimalidad (KKT) dicen que existe un "nivel" `λ` tal que `u_i'(x_i) = λ` para todo nodo con `x_i > 0`, y `u_i'(0) ≤ λ` para los demás. Cada `x_i(λ) = (u_i')⁻¹(λ)` decrece con `λ`. Basta entonces con buscar por bisección el `λ` que cumple `Σ x_i(λ) = B`. Cada iteración cuesta `O(N)` y con precisión `ε` se necesitan `O(log(1/ε))` iteraciones: `T = O(N log(1/ε))`, que **no depende del valor de B**. La misma idea con enteros (bisección sobre `λ` y luego un ajuste fino) quita la dependencia pseudo-polinomial.

### 2.5 Validación experimental (código: `experimentos_parte1.py`)

1. **Correctitud:** en 300 instancias pequeñas (N ≤ 7, B ≤ 25), el voraz coincide con un verificador exacto por programación dinámica de costo `O(N·B²)` en **300/300** casos.
2. **Conteo de operaciones** (independiente de la máquina): heapify usa unas `1.65·N` comparaciones (cota `2N`) y los pasos unas `1.1·B·log₂ N` (cota `2·B·log₂ N`). Los dos cocientes se mantienen estables desde N = 64 hasta N = 262 144.
3. **Tiempo real:** ajustando `t ≈ c₁·N + c₂·B·log₂ N` por mínimos cuadrados se obtiene R² ≈ 0.97.
   - Al variar `B` el crecimiento es lineal, como predice la teoría.
   - Al variar `N` hay una desviación a tamaños intermedios. Se explica por la **jerarquía de memoria**: cuando el heap deja de caber en la caché, cada paso cuesta más ciclos. La notación `O(·)` no modela ese efecto, y por eso el conteo de comparaciones (punto 2) es la validación limpia.
