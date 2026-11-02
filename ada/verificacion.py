"""
Verificación de restricciones de una solución.

Cada función devuelve una lista de registros {"restriccion", "cumple", "detalle"},
listos para ir al reporte de cada caso. No corrigen nada: solo revisan.
"""


def _registro(restriccion, cumple, detalle):
    return {"restriccion": restriccion, "cumple": bool(cumple), "detalle": detalle}


def _es_entero(v):
    return isinstance(v, int) and not isinstance(v, bool)


def verificar_seleccion(S, N, k):
    """Parte 2: |S| <= k, sin nodos repetidos y todos los nodos en 0..N-1. Costo O(|S|)."""
    invalidos = [i for i in S if not (_es_entero(i) and 0 <= i < N)]
    return [
        _registro("|S| <= k", len(S) <= k, f"|S| = {len(S)}, k = {k}"),
        _registro("sin nodos repetidos", len(set(S)) == len(S), f"{len(S) - len(set(S))} repetidos"),
        _registro("nodos validos (0..N-1)", not invalidos, f"invalidos: {invalidos}" if invalidos else f"N = {N}"),
    ]


def verificar_reparto(x, B):
    """Parte 1: sum x_i <= B y cada x_i entero >= 0. Costo O(len(x))."""
    malos = [v for v in x if not (_es_entero(v) and v >= 0)]
    total = sum(x)
    return [
        _registro("sum x_i <= B", total <= B, f"sum x_i = {total}, B = {B}"),
        _registro("x_i entero >= 0", not malos, f"invalidos: {malos}" if malos else "todos validos"),
    ]


def verificar_valor(nombre, reportado, recalculado, tol=1e-9):
    """El valor que devolvió el algoritmo coincide con recalcularlo desde la solución."""
    return [_registro(f"{nombre} coincide al recalcular", abs(reportado - recalculado) <= tol,
                      f"reportado = {reportado:.6f}, recalculado = {recalculado:.6f}")]


def todas_cumplen(verificaciones):
    return all(v["cumple"] for v in verificaciones)
