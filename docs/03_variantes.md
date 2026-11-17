# Variantes del proyecto — Proyecto Red (Grupo 2)

Análisis y Diseño de Algoritmos · Universidad de Caldas · Entrega final

El enunciado (§4.4) pide tres variantes obligatorias. Este documento usa la misma notación del documento de formulación ([formulacion.md](formulacion.md)) y cita sus secciones por número: la utilidad de influencia f (Definición 2), la ganancia marginal Δᵢ(S) y su cálculo en O(N) (secciones 5.5 y 5.6), el Lema 4 (f es monótona, submodular y f(∅) = 0) y el Teorema 3 (cota 1 − 1/e del voraz con solo cupo k).

- **V1: costos de participación** (esta versión).
- V2: rondas con fallas (pendiente, issue #12).
- V3: nodos vecinos (pendiente, issue #14).

Las figuras se generan con `python -m experimentos.figuras_variantes`.

---

## V1. Costos de participación

### V1.1 Planteamiento

En la Parte 2 cada nodo ocupa un lugar del cupo k, y todos los lugares valen lo mismo. En la variante V1 participar tiene un **costo** cᵢ distinto para cada nodo, y la ronda dispone de un **presupuesto de participación** P. El enunciado lo dice así: "versión con presupuesto de participación, no solo cupo k fijo", y agrega que la cota (1 − 1/e) "cambia de forma y debe redemostrarse o citarse en su versión correcta para cobertura con presupuesto (budgeted maximum coverage)".

Los casos de la profesora traen las dos restricciones a la vez: en el caso de 15 nodos, k = 5 y P = 24. Por eso planteamos la variante con **las dos restricciones** y separamos la teoría en dos regímenes, según cuál de ellas manda:

- cuando el cupo k no alcanza a restringir, el problema es exactamente la cobertura con presupuesto, y para ese caso citamos y aplicamos las cotas correctas;
- cuando el cupo k sí restringe, demostramos garantías más débiles y mostramos con un ejemplo que no puede haber una garantía constante para estos algoritmos.

La primera entrega ya respetaba el límite de costos, pero con el voraz por ganancia, que no tiene garantía (sección 8.4). Esta variante agrega dos algoritmos que sí la tienen.

### V1.2 Formalización

**Tamaño de la entrada.** N, el número de candidatos, y k, el cupo. Los costos cᵢ y el presupuesto P son números de la entrada, no parte de su tamaño: los algoritmos de esta sección hacen un número de operaciones que no depende de sus valores, solo de N y k.

**Entrada.** Los candidatos V (en una ronda, V⁽ᵗ⁾ = {i : rᵢ⁽ᵗ⁾ > 0}), la matriz de influencia W, los coeficientes aᵥ > 0, los costos cᵢ ≥ 0, el cupo k ≥ 1 y el presupuesto P ≥ 0.

**Salida.** Un grupo S ⊆ V de participantes.

**Objetivo y restricciones.**

$$
\max_{S \subseteq V} \; f(S) \qquad \text{s.a.} \qquad \sum_{i \in S} c_i \le P, \qquad |S| \le k
$$

Es el mismo programa de la sección 5.4; lo que cambia es que ahora el límite de costos es la restricción principal y buscamos algoritmos con garantía para él.

**Preprocesamiento.** Un nodo con cᵢ > P no cabe en ningún grupo factible, así que se descarta al leer la ronda. En lo que sigue suponemos cᵢ ≤ P para todo i.

**Cuántos nodos caben en P.** Definimos

$$
k_{\max}(P) = \max\left\{ |S| \; : \; S \subseteq V, \; \sum_{i \in S} c_i \le P \right\}
$$

Se calcula ordenando los costos de menor a mayor y tomando nodos mientras la suma no pase de P, en O(N log N). Es correcto porque, para cualquier tamaño j, los j nodos más baratos forman el grupo de j nodos de menor costo: si algún grupo de j nodos cabe en P, ese también cabe.

**Los dos regímenes.**

- Si k ≥ kₘₐₓ(P), ningún grupo que cumpla el presupuesto tiene más de k nodos, y la restricción |S| ≤ k sobra. El problema es **maximizar una función monótona y submodular con una restricción de mochila**, la generalización de la cobertura con presupuesto.
- Si k < kₘₐₓ(P), las dos restricciones pueden estar activas a la vez.

**El caso de la profesora.** Sus quince costos ordenados son 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7. Los siete más baratos suman 23 ≤ 24 y los ocho más baratos suman 28 > 24, así que kₘₐₓ(24) = 7 > k = 5: el cupo sí restringe. Ese caso cae en el segundo régimen.

### V1.3 NP-dureza

**Pertenencia a NP.** La versión de decisión ("¿existe S con Σᵢ∈S cᵢ ≤ P, │S│ ≤ k y f(S) ≥ t?") es la SELECCIÓN-INF de la sección 5.7, que está en NP por la sección 7.3.

**NP-dureza.** Damos dos argumentos. El primero dice que el presupuesto no hace el problema más fácil; el segundo, que con costos el problema es difícil incluso sin grafo.

1. **Por restricción a la Parte 2.** Si todos los costos valen 1 y P = k, la restricción de costos coincide con la de cupo, y la V1 es exactamente el problema de la Parte 2, que es NP-difícil por las reducciones de las secciones 7.4 y 7.5. Lo mismo vale para el régimen de solo presupuesto: si se quiere el problema de la Parte 2 con cupo h, basta tomar cᵢ = 1, P = h y un cupo de la variante k = N que no restringe.
2. **Por restricción a la mochila 0/1.** Si el grafo no tiene aristas, W es la identidad, y por la Definición 2 la utilidad queda f(S) = Σᵥ∈S aᵥ. Con k = N, la V1 es la **mochila 0/1**: elegir objetos de valor aᵥ y peso cᵥ sin pasar la capacidad P. La mochila es NP-completa (Karp, 1972; Garey y Johnson, 1979).

El segundo argumento muestra algo que la Parte 2 no tenía: con costos, el problema es difícil aunque los nodos no se influyan entre sí. Sin aristas sí existe una programación dinámica pseudo-polinomial O(N·P), pero deja de servir apenas hay influencia, porque f deja de ser aditiva.

Además, como la V1 contiene a la Cobertura Máxima, ningún algoritmo polinomial puede garantizar más de (1 − 1/e) del óptimo salvo que P = NP (Feige, 1998). El algoritmo B de la sección V1.6 alcanza justamente esa cota.

### V1.4 Por qué fallan los voraces simples

Hay dos formas naturales de adaptar el voraz de la sección 8.2. Cada una falla en un caso donde la otra acierta.

**Voraz por ganancia** (el de la primera entrega): en cada paso toma el nodo de mayor Δᵢ(S) entre los que caben. En la **instancia 1** hay un nodo X con costo 10 y f({X}) = 10, y cinco nodos Y₁, …, Y₅ con costo 2 y utilidad 9 cada uno, sin aristas, con P = 10 y k = 5. El voraz elige X (10 > 9) y ya no cabe nada más: obtiene 10, contra un óptimo de 45 (los cinco Yⱼ). La sección 8.4 demuestra que con k fijo esta razón no baja de 1/k, pero tiende a 0 cuando k crece.

**Voraz por razón**: en cada paso toma el nodo de mayor Δᵢ(S)/cᵢ entre los que caben. Corrige la instancia 1, porque los Yⱼ tienen razón 4,5 y X tiene razón 1, así que obtiene el óptimo, 45. Pero falla en la **instancia 2**: un nodo A con costo 1 y f({A}) = 2, y un nodo B con costo P y f({B}) = P, sin aristas, con k = 2. La razón de A es 2 y la de B es 1, así que el voraz toma A y después B ya no cabe (1 + P > P). Obtiene 2, contra un óptimo de P. La razón 2/P **tiende a 0** cuando P crece, aun con k = 2 fijo.

![Figura V1.1](figuras/v1_contraejemplos.png)

*Figura V1.1. Los dos contraejemplos con P = 10. Cada voraz simple falla donde el otro acierta, y el algoritmo A, que se queda con el mejor entre el voraz por razón y el mejor nodo solo, obtiene el óptimo en los dos. Los valores se calcularon con la utilidad de influencia de ada/.*

La instancia 2 muestra qué le falta al voraz por razón: un nodo caro que, por sí solo, vale mucho. La solución más simple es comparar al final con el mejor nodo individual. Eso es el algoritmo A.

### V1.5 Algoritmo A: voraz por razón con el mejor nodo individual

```text
VORAZ-RAZÓN(V, a, W, c, k, P, G)                ▷ G: grupo inicial (vacío en el algoritmo A)
1   S ← G ;  gastado ← Σᵢ∈G cᵢ
2   q[v] ← Πᵤ∈G (1 − w[u][v]) para todo v
3   mientras |S| < k:
4       mejor ← nada ;  ρmejor ← −1
5       para cada i en V \ S con gastado + cᵢ ≤ P:
6           Δ ← Σᵥ aᵥ · q[v] · w[i][v]                     ▷ O(N), sección 5.6
7           ρ ← Δ / cᵢ   (∞ si cᵢ = 0)
8           si ρ > ρmejor:  mejor ← i ;  ρmejor ← ρ
9       si mejor = nada:  terminar                         ▷ no cabe ningún candidato
10      S ← S ∪ {mejor} ;  gastado ← gastado + c_mejor
11      para cada v:  q[v] ← q[v] · (1 − w[mejor][v])        ▷ O(N)
12  devolver S

ALGORITMO-A(V, a, W, c, k, P)
1   descartar los nodos con cᵢ > P
2   S_r ← VORAZ-RAZÓN(V, a, W, c, k, P, ∅)
3   s ← argmaxᵢ∈V f({i})                                   ▷ f({i}) = Σᵥ aᵥ·w[i][v]
4   si f(S_r) ≥ f({s}):  devolver S_r
5   si no:  devolver {s}
```

En la línea 5 de VORAZ-RAZÓN el voraz no se detiene en el primer nodo que no cabe: lo salta y sigue buscando entre los que sí caben. Los empates se rompen por el índice menor, igual que en la solución base.

**Factibilidad.** El voraz solo agrega un nodo i cuando gastado + cᵢ ≤ P (línea 5) y │S│ < k (línea 3), así que Sᵣ cumple las dos restricciones al terminar. El grupo {s} también, porque se descartaron los nodos con cᵢ > P y k ≥ 1.

**Función de eficiencia.** Sea m = min(k, kₘₐₓ(P)) ≤ N, el número máximo de pasos del voraz. En el paso t se revisan a lo sumo N − t candidatos y cada uno cuesta O(N) en la línea 6, con la ganancia incremental de la sección 5.6; la línea 7 es O(1) y la actualización de la línea 11 cuesta O(N) por paso:

$$
T_{\text{razón}}(N, k) \le \sum_{t=0}^{m-1} \left[ (N - t)\cdot O(N) + O(N) \right] = O(N^2 m) = O(N^2 k)
$$

La línea 3 de ALGORITMO-A evalúa N utilidades individuales de O(N) cada una, O(N²), y el descarte de la línea 1 es O(N). En total

$$
T_A(N, k) = O(N^2 k) + O(N^2) = O(N^2 k)
$$

el mismo orden que el voraz de la solución base (sección 8.2). Comparar con el mejor nodo solo no cambia el orden del tiempo.

**Garantía.**

**Teorema V1.1 (Khuller, Moss y Naor, 1999, para cobertura; Krause y Guestrin, 2005, para f submodular).** Si f es monótona, submodular y f(∅) = 0, y la única restricción es Σᵢ∈S cᵢ ≤ P con cᵢ > 0, el algoritmo A devuelve un grupo S con

$$
f(S) \ge \frac{1}{2}\left(1 - \frac{1}{e}\right) f(O) \approx 0.316\, f(O)
$$

donde O es un grupo óptimo.

**Hipótesis en nuestro problema.** Por el Lema 4, la utilidad de influencia es monótona, submodular y cumple f(∅) = 0. La restricción de costos es la única activa cuando k ≥ kₘₐₓ(P) (sección V1.2). Los nodos con cᵢ > P se descartaron. Falta el caso cᵢ = 0, que la cita no cubre y resolvemos aparte más abajo.

Khuller, Moss y Naor demostraron el resultado para la cobertura ponderada, que es un caso particular. Nuestra f es de influencia, no de cobertura, así que la cita correcta para ella es la versión para funciones submodulares de Krause y Guestrin. Análisis posteriores dieron cotas mejores para este mismo algoritmo, por ejemplo 0,405 (Tang et al., 2021), pero aquí solo usamos la de 0,316, que es la que demostramos.

**Demostración.** Llamamos g₁, g₂, … a los nodos que el voraz por razón agrega, en ese orden, y Gⱼ = {g₁, …, gⱼ}. Sea l + 1 el primer paso en que el nodo de mayor razón entre todos los que quedan **no** cabe en el presupuesto. Lo llamamos gₗ₊₁. Hasta el paso l + 1 el voraz no ha saltado ningún nodo, así que en cada paso j ≤ l + 1 todos los nodos de O ∖ G_{j−1} eran candidatos y el voraz eligió el de mayor razón:

$$
\frac{\Delta_{g_j}(G_{j-1})}{c_{g_j}} \ge \frac{\Delta_o(G_{j-1})}{c_o} \qquad \text{para todo } o \in O \setminus G_{j-1}
$$

Por monotonía y submodularidad, como en la demostración del Teorema 3,

$$
f(O) \le f(G_{j-1} \cup O) \le f(G_{j-1}) + \sum_{o \in O \setminus G_{j-1}} \Delta_o(G_{j-1}) \le f(G_{j-1}) + \sum_{o \in O} c_o \cdot \frac{\Delta_{g_j}(G_{j-1})}{c_{g_j}}
$$

y como Σₒ∈O cₒ ≤ P, cada paso cumple

$$
\Delta_{g_j}(G_{j-1}) \ge \frac{c_{g_j}}{P}\left( f(O) - f(G_{j-1}) \right)
$$

Llamando δⱼ = f(O) − f(Gⱼ), esto dice que δⱼ ≤ (1 − c(gⱼ)/P)·δ_{j−1}. Aplicándolo l + 1 veces, con 1 − x ≤ e⁻ˣ:

$$
\delta_{l+1} \le \prod_{j=1}^{l+1}\left(1 - \frac{c_{g_j}}{P}\right) f(O) \le \exp\!\left(-\frac{1}{P}\sum_{j=1}^{l+1} c_{g_j}\right) f(O) < e^{-1} f(O)
$$

donde la última desigualdad usa que Σⱼ≤ₗ₊₁ c(gⱼ) > P, porque gₗ₊₁ no cabía. Entonces f(Gₗ₊₁) > (1 − 1/e)·f(O). El grupo Gₗ₊₁ no es factible, pero por submodularidad f(Gₗ₊₁) ≤ f(Gₗ) + f({gₗ₊₁}), así que uno de los dos sumandos vale al menos la mitad:

$$
\max\left\{ f(G_l), \; f(\{g_{l+1}\}) \right\} \ge \frac{1}{2}\left(1 - \frac{1}{e}\right) f(O)
$$

Para terminar, f(Sᵣ) ≥ f(Gₗ) por monotonía, porque Sᵣ contiene a Gₗ (después del paso l + 1 el voraz solo agrega nodos), y f({s}) ≥ f({gₗ₊₁}), porque gₗ₊₁ cabe solo en P y s es el mejor nodo individual. El algoritmo A devuelve el mayor de los dos. Si el voraz nunca encuentra un nodo que no quepa, recorre todos los candidatos y Sᵣ = V, que es óptimo por monotonía. ∎

**Nodos con costo cero.** El formato de los casos admite cᵢ = 0, y la demostración divide por cᵢ. Sea Z el conjunto de nodos de costo cero. En el régimen de solo presupuesto, por monotonía siempre conviene tomarlos todos, porque no gastan nada. El voraz los toma primero, porque su razón es ∞. Después trabaja con f′(S) = f(S ∪ Z) − f(Z), que sigue siendo monótona, submodular y con f′(∅) = 0, sobre nodos de costo positivo. Aplicando el Teorema V1.1 a f′:

$$
f(S \cup Z) = f(Z) + f'(S) \ge f(Z) + \alpha\, f'(O') \ge \alpha \left( f(Z) + f'(O') \right) = \alpha\, f(O)
$$

con α = ½(1 − 1/e) y O′ un óptimo para f′. La garantía se conserva.

### V1.6 Algoritmo B: enumeración parcial

El algoritmo A pierde la mitad del factor en el último paso de la demostración: el nodo que no cabía puede valer casi tanto como todo el grupo. El algoritmo B lo evita "adivinando" los nodos más valiosos del óptimo: prueba todos los grupos de hasta tres nodos y completa cada grupo de tres con el voraz por razón.

```text
ALGORITMO-B(V, a, W, c, k, P)
1   descartar los nodos con cᵢ > P
2   mejor ← ∅
3   para cada G ⊆ V con |G| ∈ {1, 2},  |G| ≤ k  y  Σᵢ∈G cᵢ ≤ P:
4       si f(G) > f(mejor):  mejor ← G
5   si k ≥ 3:
6       para cada G ⊆ V con |G| = 3  y  Σᵢ∈G cᵢ ≤ P:
7           S ← VORAZ-RAZÓN(V, a, W, c, k, P, G)
8           si f(S) > f(mejor):  mejor ← S
9   devolver mejor
```

**Factibilidad.** Los grupos de las líneas 3 y 6 se filtran por costo y por tamaño, y VORAZ-RAZÓN conserva las dos restricciones, como en el algoritmo A.

**Función de eficiencia.** La línea 3 revisa O(N²) grupos y evalúa cada uno en O(N) con la Definición 2: O(N³). La línea 6 revisa C(N, 3) = O(N³) grupos. Para cada uno, preparar el vector q cuesta O(N) (línea 2 de VORAZ-RAZÓN), y completarlo cuesta O(N²·k) como en el algoritmo A. Entonces

$$
T_B(N, k) = O(N^3) + O\!\left(\binom{N}{3}\right) \cdot O(N^2 k) = O(N^5 k)
$$

En el régimen de solo presupuesto el voraz puede dar hasta kₘₐₓ(P) ≤ N pasos, y el peor caso es O(N⁶). Es polinomial, pero crece rápido:

| N | Arranques C(N, 3) | Operaciones aproximadas (k = 10) |
|---|---|---|
| 15 | 455 | 10⁶ |
| 40 | 9 880 | 1,6·10⁸ |
| 150 | 551 300 | 1,2·10¹¹ |

Con N = 150 serían horas en Python. El algoritmo B es para N pequeño o mediano; el A es para instancias grandes.

**Garantía.**

**Teorema V1.2 (Khuller, Moss y Naor, 1999, para cobertura; Sviridenko, 2004, para f submodular).** Si f es monótona, submodular y f(∅) = 0, y la única restricción es Σᵢ∈S cᵢ ≤ P, el algoritmo B devuelve un grupo S con

$$
f(S) \ge \left(1 - \frac{1}{e}\right) f(O) \approx 0.632\, f(O)
$$

Las hipótesis se verifican igual que en el Teorema V1.1, con el mismo tratamiento de los nodos de costo cero. Por el resultado de Feige citado en V1.3, esta cota es la mejor posible en tiempo polinomial salvo que P = NP.

**Idea de la demostración.** Si el óptimo tiene tres nodos o menos, la línea 3 o la línea 6 lo encuentran directamente. Si tiene más, sean o₁, o₂, o₃ sus tres nodos de mayor ganancia marginal, tomados en orden voraz dentro de O. Uno de los arranques de la línea 6 es justamente G = {o₁, o₂, o₃}. Desde ahí se repite el argumento del Teorema V1.1 con la función f_G(S) = f(S ∪ G) − f(G). La diferencia está en el nodo que no cabe: como los nodos de G eran los de mayor ganancia, cualquier otro nodo de O aporta a lo sumo f(G)/3. Esa pérdida ya no se paga con la mitad del total, y la cuenta cierra en (1 − 1/e). La demostración completa está en Sviridenko (2004).

### V1.7 Cuando el cupo k también restringe

Si k < kₘₐₓ(P), como en el caso de la profesora, los Teoremas V1.1 y V1.2 no aplican. La demostración de V1.1 falla en el paso clave: el voraz puede detenerse porque llenó el cupo y no porque se acabó el presupuesto, así que la suma Σ c(gⱼ) puede quedar lejos de P y el producto ya no llega a e⁻¹. Lo que se tiene son dos restricciones de mochila a la vez: │S│ ≤ k es una mochila en la que todos los nodos pesan 1. Para ese caso existen algoritmos con garantía (1 − 1/e − ε), pero usan programación lineal y redondeo (Kulik, Shachnai y Tamir, 2009), y quedan fuera del alcance del proyecto.

Lo que sí podemos demostrar en este régimen son garantías que dependen de k.

**Lema V1.3.** Si f es monótona, submodular y f(∅) = 0, es **subaditiva**: f(A ∪ B) ≤ f(A) + f(B).

**Demostración.** Sea B ∖ A = {b₁, …, bₘ} y Bⱼ = {b₁, …, bⱼ}, con B₀ = ∅. Escribimos la diferencia como una suma telescópica y aplicamos la submodularidad a cada término, usando que Bⱼ₋₁ ⊆ A ∪ Bⱼ₋₁:

$$
f(A \cup B) - f(A) = \sum_{j=1}^{m} \Delta_{b_j}(A \cup B_{j-1}) \le \sum_{j=1}^{m} \Delta_{b_j}(B_{j-1}) = f(B \setminus A) - f(\emptyset) \le f(B)
$$

donde el último paso usa f(∅) = 0 y la monotonía (B ∖ A ⊆ B). ∎

**Teorema V1.4.** Con las dos restricciones activas, y siendo O un grupo óptimo:

$$
f(S_A) \ge \frac{1}{k}\, f(O), \qquad f(S_B) \ge \frac{1}{\lceil k/3 \rceil}\, f(O)
$$

**Demostración.** O tiene a lo sumo k nodos y cada uno cabe solo en P. Por el Lema V1.3, f(O) ≤ Σₒ∈O f({o}) ≤ k·f({s}), donde s es el mejor nodo individual, y el algoritmo A devuelve al menos f({s}). Para el algoritmo B, partimos O en ⌈k/3⌉ grupos de a lo sumo tres nodos. Cada grupo es factible, porque es un subconjunto de O, y lo revisan las líneas 3 o 6 de ALGORITMO-B, así que f(S_B) es al menos el valor del mejor grupo. Otra vez por el Lema V1.3, f(O) ≤ ⌈k/3⌉·máx_grupo f(grupo). ∎

En el caso de la profesora (k = 5) esto da al menos 20 % del óptimo para A y al menos 50 % para B. Si k ≤ 3, el algoritmo B es exacto.

**La garantía de A no puede ser mejor que 1/k.** Tomamos k nodos baratos con cᵢ = 1 y f({i}) = 1, y k nodos caros con cᵢ = P/k y f({i}) = P/(2k), sin aristas, con P = 2k². Los baratos tienen razón 1 y los caros 1/2, así que el voraz por razón toma los k baratos, llena el cupo y obtiene k. El mejor nodo solo vale P/(2k) = k. El óptimo toma los k caros: cuestan exactamente P y valen P/2 = k². La razón del algoritmo A es k/k² = 1/k, que tiende a 0 cuando k crece. Lo comprobamos con la fuerza bruta para k = 3, 4 y 6, con razones de 0,333, 0,25 y 0,167. En ese mismo ejemplo el algoritmo B obtiene 9 de 9 con k = 3, 13 de 16 con k = 4 y 21 de 36 con k = 6, siempre por encima de su cota 1/⌈k/3⌉.

Por eso, en el régimen mixto, la evaluación de la V1 es experimental: en la implementación (issue #11) se compararán los dos algoritmos y el voraz por ganancia contra la fuerza bruta en cientos de instancias pequeñas, con k restrictivo y sin él.

### V1.8 Algoritmo exacto de referencia

La fuerza bruta de la sección 8.1 ya contempla las dos restricciones: revisa todos los grupos de tamaño 1 a k y descarta los que pasan de P. Su tiempo es

$$
T_{FB}(N, k) = O\left( N k \sum_{j=0}^{k} \binom{N}{j} \right)
$$

y es el juez contra el que se miden los algoritmos A y B. En el régimen de solo presupuesto, el tamaño máximo que vale la pena revisar es kₘₐₓ(P) y no k.

### V1.9 Resumen

| Algoritmo | Tiempo | Garantía si k ≥ kₘₐₓ(P) | Garantía si k < kₘₐₓ(P) |
|---|---|---|---|
| Voraz por ganancia (primera entrega) | O(N²·k) | ninguna constante (sección 8.4) | 1/k |
| Voraz por razón, solo | O(N²·k) | ninguna (instancia 2: 2/P → 0) | ninguna |
| **A**: voraz por razón + mejor nodo | O(N²·k) | ½(1 − 1/e) ≈ 0,316 (Teorema V1.1) | 1/k (Teorema V1.4) |
| **B**: enumeración parcial | O(N⁵·k) | 1 − 1/e ≈ 0,632 (Teorema V1.2), la mejor posible | 1/⌈k/3⌉ (Teorema V1.4); exacto si k ≤ 3 |
| Fuerza bruta | O(N·k·Σⱼ≤ₖ C(N, j)) | exacto | exacto |

Comprobamos los números de esta sección con la fuerza bruta antes de escribirlos. En 300 instancias de 6 a 10 nodos donde el cupo no restringe, el algoritmo A nunca bajó de 0,768 del óptimo y el algoritmo B lo encontró siempre. En otras 300 con el cupo restringiendo (k entre 2 y 6), el peor caso fue 0,529 para A y 0,984 para B, sin violar ninguna de las dos cotas del Teorema V1.4. Los experimentos completos, con tiempos medidos y al menos cinco tamaños de N, son parte de la issue #11.

### Referencias de la variante V1

- Feige, U. (1998). A threshold of ln n for approximating set cover. *Journal of the ACM*, 45(4), 634–652.
- Garey, M. R. y Johnson, D. S. (1979). *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W. H. Freeman.
- Karp, R. M. (1972). Reducibility among combinatorial problems. En R. E. Miller y J. W. Thatcher (Eds.), *Complexity of Computer Computations* (pp. 85–103). Plenum Press.
- Khuller, S., Moss, A. y Naor, J. (1999). The budgeted maximum coverage problem. *Information Processing Letters*, 70(1), 39–45.
- Krause, A. y Guestrin, C. (2005). *A note on the budgeted maximization of submodular functions* (CMU-CALD-05-103). Carnegie Mellon University.
- Kulik, A., Shachnai, H. y Tamir, T. (2009). Maximizing submodular set functions subject to multiple linear constraints. En *Proceedings of the 20th ACM-SIAM Symposium on Discrete Algorithms (SODA)*, 545–554.
- Sviridenko, M. (2004). A note on maximizing a submodular set function subject to a knapsack constraint. *Operations Research Letters*, 32(1), 41–43.
- Tang, J., Tang, X., Lim, A., Han, K., Li, C. y Yuan, J. (2021). Revisiting modified greedy algorithm for monotone submodular maximization with a knapsack constraint. *Proceedings of the ACM on Measurement and Analysis of Computing Systems*, 5(1), 1–22.
