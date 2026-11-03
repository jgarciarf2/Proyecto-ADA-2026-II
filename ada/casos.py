"""
Casos de prueba: convertir el formato JSON de un caso a los datos que usan los
algoritmos, y el resultado de una ronda a un diccionario que se puede guardar.

Formato PROVISIONAL de un caso (cuando llegue el de la profesora solo cambia leer_caso):

    {
      "nombre": "caso_01",
      "k": 4,
      "B": 20,
      "pesos_tipos": [3.1, 2.0, ...],                 # peso w_e del tipo e = 0..M-1
      "nodos": [
        {"id": "n0", "tipos": [5, 12, 13],
         "utilidad": {"familia": "log", "a": 1.82}},  # log | sqrt | exp (con "b") | tabla
        {"id": "n1", "tipos": [0, 4],
         "utilidad": {"familia": "tabla", "valores": [0, 2.0, 3.5, 4.5]}},
        ...
      ]
    }

Este módulo no lee ni escribe archivos: recibe y devuelve diccionarios.
"""
import math
from dataclasses import dataclass

from ada.generadores import instancia_cobertura, instancia_reparto
from ada.parte2.fuerza_bruta import fuerza_bruta
from ada.utilidades import UtilidadLog, UtilidadRaiz, UtilidadSaturacion, UtilidadTabla

LIMITE_FUERZA_BRUTA = 200_000      # C(N, k) máximo para calcular el óptimo exacto
LIMITE_TRAZA_POR_UNIDAD = 5_000    # con B mayor solo se guarda el resumen del reparto


@dataclass
class Caso:
    nombre: str
    ids: list            # id original de cada nodo; internamente el nodo i es ids[i]
    conjuntos: list      # conjuntos[i] = frozenset de tipos que cubre el nodo i
    pesos: list          # pesos[e] = w_e
    utilidades: list     # utilidades[i] = utilidad cóncava del nodo i
    k: int
    B: int

    @property
    def N(self):
        return len(self.ids)

    @property
    def M(self):
        return len(self.pesos)


class CasoInvalido(ValueError):
    """El caso no cumple el formato o las condiciones del problema."""


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def leer_caso(datos):
    """Valida el diccionario de un caso y lo convierte en un Caso. Costo O(N·d + M)."""
    for campo in ("k", "B", "pesos_tipos", "nodos"):
        if campo not in datos:
            raise CasoInvalido(f"falta el campo '{campo}'")
    k, B = datos["k"], datos["B"]
    pesos = [float(w) for w in datos["pesos_tipos"]]
    nodos = datos["nodos"]
    if not (isinstance(k, int) and k >= 1):
        raise CasoInvalido("k debe ser un entero >= 1")
    if not (isinstance(B, int) and B >= 0):
        raise CasoInvalido("B debe ser un entero >= 0")
    if not nodos:
        raise CasoInvalido("el caso no tiene nodos")
    if any(w <= 0 for w in pesos):
        raise CasoInvalido("todos los pesos de los tipos deben ser > 0")

    ids, conjuntos, utilidades = [], [], []
    for pos, nodo in enumerate(nodos):
        ident = nodo.get("id", pos)
        tipos = nodo.get("tipos", [])
        malos = [e for e in tipos if not (isinstance(e, int) and 0 <= e < len(pesos))]
        if malos:
            raise CasoInvalido(f"nodo {ident}: tipos fuera de 0..{len(pesos) - 1}: {malos}")
        ids.append(ident)
        conjuntos.append(frozenset(tipos))
        utilidades.append(_leer_utilidad(nodo.get("utilidad"), ident))
    if len(set(map(str, ids))) != len(ids):
        raise CasoInvalido("hay ids de nodo repetidos")
    return Caso(datos.get("nombre", "caso"), ids, conjuntos, pesos, utilidades, k, B)


def _leer_utilidad(u, ident):
    if not isinstance(u, dict) or "familia" not in u:
        raise CasoInvalido(f"nodo {ident}: falta 'utilidad' con su 'familia'")
    familia = u["familia"]
    if familia == "tabla":
        valores = [float(v) for v in u.get("valores", [])]
        if len(valores) < 2 or valores[0] != 0:
            raise CasoInvalido(f"nodo {ident}: la tabla necesita al menos 2 valores y empezar en 0")
        ganancias = [b - a for a, b in zip(valores, valores[1:])]
        if any(g < 0 for g in ganancias):
            raise CasoInvalido(f"nodo {ident}: la tabla no es creciente")
        if any(g2 > g1 + 1e-12 for g1, g2 in zip(ganancias, ganancias[1:])):
            raise CasoInvalido(f"nodo {ident}: la tabla no es cóncava (una ganancia marginal sube)")
        return UtilidadTabla(valores)
    a = float(u.get("a", 0))
    if a <= 0:
        raise CasoInvalido(f"nodo {ident}: 'a' debe ser > 0")
    if familia == "log":
        return UtilidadLog(a)
    if familia == "sqrt":
        return UtilidadRaiz(a)
    if familia == "exp":
        b = float(u.get("b", 0))
        if b <= 0:
            raise CasoInvalido(f"nodo {ident}: 'b' debe ser > 0")
        return UtilidadSaturacion(a, b)
    raise CasoInvalido(f"nodo {ident}: familia desconocida '{familia}' (log, sqrt, exp o tabla)")


def utilidad_a_dict(u):
    if isinstance(u, UtilidadLog):
        return {"familia": "log", "a": u.a}
    if isinstance(u, UtilidadRaiz):
        return {"familia": "sqrt", "a": u.a}
    if isinstance(u, UtilidadSaturacion):
        return {"familia": "exp", "a": u.a, "b": u.b}
    if isinstance(u, UtilidadTabla):
        return {"familia": "tabla", "valores": u.valores}
    raise TypeError(f"utilidad sin formato: {u!r}")


def caso_sintetico(nombre, N, M, d, k, B, semilla=0):
    """Caso en el formato JSON, generado con los mismos generadores de los experimentos."""
    cob = instancia_cobertura(N, M, d, semilla=semilla)
    rep = instancia_reparto(N, B, semilla=semilla)
    return {
        "nombre": nombre, "k": k, "B": B,
        "pesos_tipos": [round(w, 4) for w in cob.pesos],
        "nodos": [{"id": f"n{i}", "tipos": sorted(c), "utilidad": utilidad_a_dict(u)}
                  for i, (c, u) in enumerate(zip(cob.conjuntos, rep.utilidades))],
    }


# ---------------------------------------------------------------------------
# Óptimo de referencia y resultado
# ---------------------------------------------------------------------------
def optimo_si_es_factible(caso, limite=LIMITE_FUERZA_BRUTA):
    """Óptimo exacto de la selección por fuerza bruta, solo si C(N, k) <= limite; si no, None."""
    if math.comb(caso.N, min(caso.k, caso.N)) > limite:
        return None
    S, valor = fuerza_bruta(caso.conjuntos, caso.pesos, caso.k)
    return {"valor": valor, "seleccion": [caso.ids[i] for i in S], "metodo": "fuerza bruta"}


def resultado_a_dict(caso, r, optimo=None):
    """
    Pasa el resultado de resolver_ronda a un diccionario serializable, con los ids
    originales de los nodos. Con B > LIMITE_TRAZA_POR_UNIDAD la traza del reparto
    por unidad se omite y queda el resumen por nodo.
    """
    ident = caso.ids
    traza_completa = caso.B <= LIMITE_TRAZA_POR_UNIDAD
    return {
        "caso": caso.nombre,
        "N": caso.N, "k": caso.k, "B": caso.B, "M": caso.M,
        "seleccion": [ident[i] for i in r["seleccion"]],
        "utilidad_conjunta": r["utilidad_conjunta"],
        "utilidad_reparto": r["utilidad_reparto"],
        "optimo": optimo,
        "reparto": [{**fila, "nodo": ident[fila["nodo"]]} for fila in r["resumen_reparto"]],
        "verificaciones": r["verificaciones"],
        "cumple_todo": r["cumple_todo"],
        "tiempo_s": r["tiempo_s"],
        "traza_seleccion": [{**p, "nodo": ident[p["nodo"]]} for p in r["traza_seleccion"]],
        "traza_reparto_completa": traza_completa,
        "traza_reparto": [{**p, "nodo": ident[p["nodo"]]} for p in r["traza_reparto"]] if traza_completa else [],
    }
