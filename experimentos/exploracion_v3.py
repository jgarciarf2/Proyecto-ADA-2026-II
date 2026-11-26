"""
Exploración de la variante V3 (efecto de nodos vecinos), docs/03_variantes.md §V3.4 y §V3.10.

PROTOTIPO DE REFERENCIA: genera los números exploratorios de la sección V3. No es la
implementación oficial; esa va en ada/variantes/vecinos.py (issue #15), con su propio
voraz perezoso, pruebas y experimentos. Aquí los algoritmos se escriben de la forma más
directa posible (cada ganancia recalcula U completa) para que sean fáciles de revisar.

Modelo:  y_i = x_i + alpha * sum_{j != i} w_ij x_j ;   U(x) = sum_i a_i ln(1 + y_i)
Restricciones: sum x_i <= B, 0 <= x_i <= r_i, enteros.

Compara, contra el óptimo por enumeración:
  - voraz "ciego" de la Parte 1 (ignora a los vecinos)
  - voraz por unidades con la ganancia real (voraz V3)
  - voraz V3 + búsqueda local por transferencias de una unidad

Ejecutar desde la raíz:  python -m experimentos.exploracion_v3
"""
import itertools
import math
import random
import time


def y_de(x, W, alpha):
    k = len(x)
    return [x[i] + alpha * sum(W[i][j] * x[j] for j in range(k) if j != i) for i in range(k)]


def U(x, a, W, alpha):
    return sum(ai * math.log1p(yi) for ai, yi in zip(a, y_de(x, W, alpha)))


def marginal(j, x, a, W, alpha):
    x2 = list(x); x2[j] += 1
    return U(x2, a, W, alpha) - U(x, a, W, alpha)


def voraz(a, W, alpha, r, B):
    k = len(a); x = [0] * k
    for _ in range(B):
        mejor, g = None, 0.0
        for j in range(k):
            if x[j] < r[j]:
                d = marginal(j, x, a, W, alpha)
                if d > g + 1e-12:
                    mejor, g = j, d
        if mejor is None:
            break
        x[mejor] += 1
    return x, U(x, a, W, alpha)


def separable(a, r, B):
    """El voraz de la Parte 1 'ciego' a los vecinos (alpha = 0)."""
    return voraz(a, [[0] * len(a) for _ in a], 0.0, r, B)[0]


def busqueda_local(x, a, W, alpha, r):
    x = list(x); k = len(x); v = U(x, a, W, alpha); mejora = True; pasos = 0
    while mejora:
        mejora = False
        for i in range(k):
            for j in range(k):
                if i != j and x[i] > 0 and x[j] < r[j]:
                    x[i] -= 1; x[j] += 1
                    nv = U(x, a, W, alpha)
                    if nv > v + 1e-12:
                        v, mejora, pasos = nv, True, pasos + 1
                    else:
                        x[i] += 1; x[j] -= 1
    return x, v, pasos


def composiciones(k, total, r):
    if k == 1:
        if total <= r[0]:
            yield (total,)
        return
    for x0 in range(min(total, r[0]) + 1):
        for resto in composiciones(k - 1, total - x0, r[1:]):
            yield (x0,) + resto


def exacto(a, W, alpha, r, B):
    # U es monótona para alpha >= 0, así que basta con usar exactamente min(B, sum r) unidades
    total = min(B, sum(r))
    mejor, mv = None, -1
    for x in composiciones(len(a), total, r):
        v = U(x, a, W, alpha)
        if v > mv:
            mejor, mv = x, v
    return list(mejor), mv


def instancia(rng, k, densidad=1.0):
    a = [round(rng.uniform(5, 13), 1) for _ in range(k)]
    W = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(i + 1, k):
            if rng.random() < densidad:
                W[i][j] = W[j][i] = round(rng.choice(range(5, 90, 5)) / 100, 2)
    return a, W


def buscar_contraejemplo():
    """Contraejemplo pequeño con números redondos."""
    mejores = []
    for a1, a2 in itertools.product(range(1, 11), repeat=2):
        for w in (0.5, 1.0):
            for alpha in (0.5, 1.0):
                for B in (2, 3, 4):
                    a = [a1, a2]; W = [[0, w], [w, 0]]; r = [B, B]
                    xg, vg = voraz(a, W, alpha, r, B)
                    xo, vo = exacto(a, W, alpha, r, B)
                    if vo - vg > 1e-9:
                        mejores.append((vg / vo, a, w, alpha, B, xg, vg, xo, vo))
    mejores.sort(key=lambda t: t[0])
    return mejores


def experimento_calidad(semillas=200):
    print("alpha | k | inst | voraz_V3: %opt  min_razon  media | sep(ciego): min media | +BL: %opt min")
    for alpha in (0.0, 0.1, 0.25, 0.5, 1.0):
        for k in (3, 4, 5):
            stats = {"g": [], "s": [], "l": []}
            optg = optl = 0
            for s in range(semillas):
                rng = random.Random(1000 * k + s)
                a, W = instancia(rng, k, densidad=rng.choice([0.3, 0.6, 1.0]))
                B = rng.randint(4, 14)
                r = [rng.randint(2, 10) for _ in range(k)]
                xo, vo = exacto(a, W, alpha, r, B)
                xg, vg = voraz(a, W, alpha, r, B)
                xs = separable(a, r, B); vs = U(xs, a, W, alpha)
                xl, vl, _ = busqueda_local(xg, a, W, alpha, r)
                stats["g"].append(vg / vo); stats["s"].append(vs / vo); stats["l"].append(vl / vo)
                optg += vo - vg < 1e-9; optl += vo - vl < 1e-9
            n = semillas
            print(f"{alpha:5} | {k} | {n} | {100*optg/n:5.1f}%  {min(stats['g']):.5f}  {sum(stats['g'])/n:.5f} | "
                  f"{min(stats['s']):.5f} {sum(stats['s'])/n:.5f} | {100*optl/n:5.1f}% {min(stats['l']):.5f}")


def caso_profesora():
    import json
    from pathlib import Path
    from ada.casos_red import leer_caso_red
    ruta = Path(__file__).resolve().parents[1] / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
    datos = json.loads(ruta.read_text(encoding="utf8"))
    c = leer_caso_red(datos)
    S = [c.ids.index(n) for n in ["N11", "N14", "N09", "N15", "N13"]]
    a = [c.a[i] for i in S]
    W = [[c.W[i][j] if i != j else 0.0 for j in S] for i in S]
    r = [18] * 5
    print("caso profesora, ronda 1, S =", [c.ids[i] for i in S], "a =", a)
    for alpha in (0.0, 0.1, 0.25, 0.5, 1.0):
        t0 = time.perf_counter(); xg, vg = voraz(a, W, alpha, r, 30); tg = time.perf_counter() - t0
        xs = separable(a, r, 30); vs = U(xs, a, W, alpha)
        t0 = time.perf_counter(); xo, vo = exacto(a, W, alpha, r, 30); to = time.perf_counter() - t0
        xl, vl, p = busqueda_local(xg, a, W, alpha, r)
        print(f"alpha={alpha}: sep {xs} {vs:.4f} | voraz {xg} {vg:.4f} ({tg*1e3:.2f} ms) | +BL {xl} {vl:.4f} ({p} pasos)"
              f" | exacto {xo} {vo:.4f} ({to:.1f} s)")


def peor_caso_dirigido():
    """Busca instancias donde el voraz V3 quede peor; alpha grande, grafos estrella."""
    peor = (1, None)
    for s in range(3000):
        rng = random.Random(s)
        k = rng.choice([3, 4])
        a = [rng.choice([1, 2, 5, 10, 20]) for _ in range(k)]
        W = [[0.0] * k for _ in range(k)]
        for i in range(k):
            for j in range(i + 1, k):
                if rng.random() < 0.6:
                    W[i][j] = W[j][i] = rng.choice([0.25, 0.5, 1.0])
        alpha = rng.choice([0.5, 1.0, 2.0, 4.0])
        B = rng.randint(2, 8); r = [rng.randint(1, 6) for _ in range(k)]
        vo = exacto(a, W, alpha, r, B)[1]; vg = voraz(a, W, alpha, r, B)[1]
        if vo > 0 and vg / vo < peor[0]:
            peor = (vg / vo, (a, W, alpha, B, r))
    print("peor razón encontrada (búsqueda dirigida, alpha hasta 4):", peor)


if __name__ == "__main__":
    ce = buscar_contraejemplo()
    print("contraejemplos k=2:", len(ce))
    for t in ce[:8]:
        print(t)
    experimento_calidad()
    caso_profesora()
    peor_caso_dirigido()
