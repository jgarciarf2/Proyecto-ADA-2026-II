# Parte 2 — Selección de nodos participantes

## 1. El problema

Recordatorio de la formalización (ver `01_formalizacion_y_parte1.md`, §1.2):

- **Entrada:** `N` nodos. El nodo `i` cubre un conjunto `D_i` de "tipos de datos" tomados de un universo de `M` tipos, y cada tipo `e` tiene un peso `w_e > 0`. Además, un cupo `k < N`.
- **Utilidad conjunta (cobertura ponderada):** `f(S) = Σ_{e ∈ ∪_{i∈S} D_i} w_e`, el peso total de los tipos cubiertos por al menos un nodo de `S`.
- **Objetivo:** encontrar `S ⊆ {1..N}` con `|S| ≤ k` que maximice `f(S)`.
- **Versión de decisión (SELECCIÓN-DEC):** dado además un umbral `t`, ¿existe `S` con `|S| ≤ k` y `f(S) ≥ t`?

En nuestras instancias cada nodo cubre exactamente `d` tipos, así que `|D_i| = d`.

---

## 2. La utilidad es monótona y submodular

**Lema 1.** La cobertura ponderada `f` cumple:
- `f(∅) = 0`;
- es **monótona**: `A ⊆ A' ⇒ f(A) ≤ f(A')`;
- es **submodular**: para `A ⊆ A'` y `v ∉ A'`, `f(A ∪ {v}) − f(A) ≥ f(A' ∪ {v}) − f(A')`.

**Demostración.** Llamemos `C(A) = ∪_{i∈A} D_i` a los tipos cubiertos por `A`.

- `f(∅) = 0`: con ningún nodo no hay nada cubierto.
- **Monotonía:** si `A ⊆ A'`, entonces `C(A) ⊆ C(A')`. Como todos los pesos son positivos, sumar sobre un conjunto más grande no puede dar menos.
- **Submodularidad:** lo que aporta `v` son los tipos nuevos que trae, `f(A ∪ {v}) − f(A) = Σ_{e ∈ D_v \ C(A)} w_e`. Como `C(A) ⊆ C(A')`, los tipos que son nuevos para `A'` también son nuevos para `A`: `D_v \ C(A') ⊆ D_v \ C(A)`. Por lo tanto, la ganancia respecto a `A'` es menor o igual que la ganancia respecto a `A`. ∎

> **En palabras:** un nodo nuevo aporta menos cuanto más cubierto está ya el universo, porque muchos de sus datos ya los tiene alguien más. Son los rendimientos decrecientes de la Parte 1, pero ahora sobre conjuntos.

Además, el programa verifica estas propiedades con 2 000 pruebas aleatorias en `experimentos_parte2.py` y obtiene 0 violaciones.

---

## 3. NP-dureza: reducción desde Cobertura Máxima

**Problema de origen, COBERTURA-MÁXIMA (decisión).** Dados un universo `U`, subconjuntos `S_1, …, S_N ⊆ U` y enteros `k` y `t`, ¿existen `k` subconjuntos cuya unión tenga al menos `t` elementos?

Este problema es NP-completo. Se sabe por la reducción desde **Cobertura de Conjuntos** (SET-COVER, uno de los 21 problemas de Karp, 1972): `U` se puede cubrir con `k` conjuntos si y solo si la Cobertura Máxima con umbral `t = |U|` es positiva.

### 3.1 Construcción (la función `reducir_desde_cobertura_maxima` del código)

Dada una instancia `(U, S_1..S_N, k, t)` de COBERTURA-MÁXIMA, se construye una instancia de SELECCIÓN-DEC así:

| Cobertura Máxima | → | Selección de participantes |
|---|---|---|
| cada subconjunto `S_i` | → | un nodo `i` con `D_i = S_i` |
| cada elemento `e ∈ U` | → | un tipo de datos con peso `w_e = 1` |
| `k` | → | el mismo cupo `k` |
| `t` | → | el mismo umbral `t` |

Con pesos 1, la utilidad es `f(A) = |∪_{i∈A} S_i|`: **el número de elementos cubiertos**.

**Tiempo de la construcción:** se recorre `U` una vez y cada `S_i` una vez, así que cuesta `O(|U| + Σ|S_i|)`, que es polinomial (de hecho lineal) en el tamaño de la instancia original.

### 3.2 Equivalencia (las dos direcciones)

- **(⇒)** Si la instancia de Cobertura Máxima es positiva, hay índices `i_1..i_k` con `|S_{i_1} ∪ … ∪ S_{i_k}| ≥ t`. Tomamos `A = {i_1..i_k}`. Entonces `|A| = k` y `f(A) = |∪ S_{i_j}| ≥ t`, así que la instancia de Selección es positiva.
- **(⇐)** Si la instancia de Selección es positiva, hay un `A` con `|A| ≤ k` y `f(A) ≥ t`, es decir, `|∪_{i∈A} S_i| ≥ t`. Si `|A| < k`, completamos con subconjuntos cualesquiera hasta tener `k`; por monotonía la unión no se achica. Así obtenemos `k` subconjuntos que cubren al menos `t` elementos, y la instancia de Cobertura Máxima es positiva.

### 3.3 Conclusión

Tenemos `COBERTURA-MÁXIMA ≤p SELECCIÓN-DEC`. Si existiera un algoritmo polinomial para Selección, resolveríamos Cobertura Máxima en tiempo polinomial: primero transformamos, luego resolvemos. Como Cobertura Máxima es NP-difícil, **SELECCIÓN-DEC es NP-difícil**, y la versión de optimización también lo es, porque resolverla responde la de decisión comparando `f(S*) ≥ t`.

Además, SELECCIÓN-DEC (con `f` de cobertura) está en **NP**: un certificado es el conjunto `S`, y verificar `|S| ≤ k` y `f(S) ≥ t` cuesta `O(k·d)`. Por eso, con utilidad de cobertura el problema es **NP-completo**.

> **Para la sustentación:** "Cobertura Máxima es un caso particular de nuestro problema: basta poner peso 1 a cada elemento. Si pudiéramos resolver el nuestro rápido, resolveríamos Cobertura Máxima rápido, y eso no se sabe hacer."
>
> **Ojo con la dirección.** Se reduce **desde** el problema conocido como difícil **hacia** el nuestro. Hacerlo al revés no demuestra nada.

**Ejemplo pequeño.** Sea `U = {1..6}`, con `S_1 = {1,2,3}`, `S_2 = {4,5,6}` y `S_3 = {1,2,4,5}`, `k = 2` y `t = 6`. La respuesta es sí: `S_1 ∪ S_2 = U`. En la instancia construida, los nodos 1 y 2 dan `f = 6 ≥ t`.

---

## 4. Algoritmo exacto de referencia: fuerza bruta

Se prueban todos los subconjuntos de exactamente `k` nodos. Por monotonía, el óptimo siempre se alcanza con `k` nodos.

- Hay `C(N, k)` subconjuntos, y evaluar `f` en cada uno cuesta `O(k·d)` (unir `k` conjuntos de tamaño `d`).
- Total: `T_FB(N, k) = O(C(N, k) · k · d)`.
- Con `k = N/2`, se tiene `C(N, N/2) ≥ 2^N / (N+1)`, así que la fuerza bruta es **exponencial**.
- Solo sirve en instancias pequeñas, para verificar la cota del voraz.

---

## 5. El algoritmo aproximado: voraz submodular

```
VORAZ-SELECCIÓN(D_1..D_N, w, k):
1  S ← ∅ ;  cubiertos ← ∅
2  repetir k veces:
3      para cada nodo i ∉ S:                              // N − |S| nodos
4          g_i ← Σ_{e ∈ D_i, e ∉ cubiertos} w_e           // ganancia marginal, τ = O(d)
5      j ← argmax g_i
6      S ← S ∪ {j} ;  cubiertos ← cubiertos ∪ D_j          // O(d)
7  devolver S
```

### 5.1 Función de eficiencia (contando operaciones)

- **Costo de una evaluación (`τ`):** la línea 4 recorre los `d` elementos de `D_i` y, para cada uno, consulta si está en `cubiertos`. Esa consulta cuesta `O(1)` porque `cubiertos` es una tabla hash. Por lo tanto `τ = O(d)`.
- **Evaluaciones totales:** en el paso `t` (contando desde 0) quedan `N − t` candidatos, así que

  `E(N, k) = Σ_{t=0}^{k−1} (N − t) = kN − k(k−1)/2 ≤ N·k`.

- **Actualización (línea 6):** `O(d)` por paso, es decir, `O(k·d)` en total, que es menor que lo anterior.

```
T(N, k) = E(N, k)·τ + O(k·d) = O(N · k · d)
```

Es **polinomial**, frente a `C(N, k)` de la fuerza bruta. Medido en el tamaño real de la entrada, `L = Σ|D_i| = N·d`, queda `T = O(k · L)`.

### 5.2 Garantía de aproximación (1 − 1/e)

**Teorema (Nemhauser, Wolsey y Fisher, 1978).** Si `f` es monótona, submodular y `f(∅) = 0`, el voraz que en cada uno de los `k` pasos agrega el elemento de mayor ganancia marginal devuelve un `S` con

  `f(S) ≥ (1 − (1 − 1/k)^k) · f(OPT) ≥ (1 − 1/e) · f(OPT) ≈ 0.632 · f(OPT)`.

**Aplicación a nuestro caso.** El Lema 1 demuestra que nuestra `f` cumple exactamente las tres hipótesis. Por eso el teorema aplica.

**Idea de la demostración** (útil para defenderla). Sea `S_t` el conjunto del voraz tras `t` pasos, `O` el óptimo, y `δ_t = f(O) − f(S_t)` lo que falta para llegar al óptimo.

1. Por monotonía, `f(O) ≤ f(S_t ∪ O)`.
2. Por submodularidad, agregar los `k` elementos de `O` a `S_t` uno por uno aporta a lo sumo la suma de sus ganancias individuales respecto a `S_t`: `f(S_t ∪ O) ≤ f(S_t) + Σ_{o∈O} [f(S_t ∪ {o}) − f(S_t)]`.
3. Cada una de esas `k` ganancias es menor o igual que la que eligió el voraz: `≤ f(S_t) + k·[f(S_{t+1}) − f(S_t)]`.
4. Juntando 1–3: `δ_t ≤ k·(δ_t − δ_{t+1})`, es decir, `δ_{t+1} ≤ (1 − 1/k)·δ_t`. **En cada paso, lo que falta se reduce al menos en un factor `(1 − 1/k)`.**
5. Partiendo de `δ_0 = f(O)`: `δ_k ≤ (1 − 1/k)^k · f(O) ≤ e^{−1} · f(O)`, porque `1 − x ≤ e^{−x}`. Luego `f(S_k) ≥ (1 − 1/e)·f(OPT)`. ∎

**La cota no se puede mejorar en general.** Feige (1998) demostró que, a menos que P = NP, ningún algoritmo polinomial aproxima Cobertura Máxima mejor que `(1 − 1/e)`. El voraz es, en ese sentido, lo mejor posible.

### 5.3 El voraz no siempre es óptimo

Con la instancia del ejemplo de §3 (`k = 2`), el voraz toma primero `S_3 = {1,2,4,5}`, que es el más grande (4 elementos). Después cualquier otro conjunto solo agrega 1 elemento, así que termina con `f = 5`. El óptimo es `S_1 ∪ S_2 = 6`. La razón es `5/6 ≈ 0.83`, que es mayor que 0.632, como garantiza el teorema.

---

## 6. Validación experimental (`experimentos_parte2.py`)

| Experimento | Resultado |
|---|---|
| Monotonía y submodularidad (2 000 pruebas aleatorias) | 0 violaciones |
| Cota `(1 − 1/e)` en 500 instancias pequeñas con mucho traslape (fuerza bruta como referencia) | **todas cumplen**. Razón mínima observada ≈ 0.82, y el voraz fue exactamente óptimo en ~80 % de los casos |
| Conteo de evaluaciones de ganancia marginal | coincide **exactamente** con `kN − k(k−1)/2` en todos los tamaños |
| Tiempo del voraz al variar `N` (k = 20) y `k` (N = 2 000) | crecimiento lineal en cada variable. El cociente `t / (N·k·d)` se mantiene casi constante |
| Voraz contra fuerza bruta con `k = N/2`, para N de 8 a 22 | la fuerza bruta crece exponencialmente (de 0.2 ms a 2 s, una recta en escala logarítmica); el voraz se mantiene por debajo de 1 ms |

La cota `(1 − 1/e)` es una garantía para el **peor caso**. En instancias aleatorias el voraz suele quedar muy por encima. La desigualdad del teorema es ajustada solo en instancias construidas a propósito.

---

## Referencias

- Nemhauser, G. L., Wolsey, L. A., & Fisher, M. L. (1978). An analysis of approximations for maximizing submodular set functions—I. *Mathematical Programming*, 14(1), 265–294.
- Karp, R. M. (1972). Reducibility among combinatorial problems. En *Complexity of Computer Computations* (pp. 85–103). Plenum Press.
- Feige, U. (1998). A threshold of ln n for approximating set cover. *Journal of the ACM*, 45(4), 634–652.
