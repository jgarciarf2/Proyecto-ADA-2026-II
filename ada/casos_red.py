"""
Lectura del formato de casos de la profesora (Grupo 2 · Red):

    {"parametros": {"numero_nodos", "numero_rondas", "cupo_participantes_por_ronda_k",
                    "presupuesto_ruido_por_ronda_B", "presupuesto_costos_participacion_por_ronda"},
     "grafo": [{"u", "v", "peso_influencia"}, ...],
     "nodos": [{"id", "coeficiente_utilidad", "presupuesto_total_nodo", "costo_participacion"}, ...]}

SUPUESTOS PROVISIONALES (sin confirmar con la profesora):
  - utilidad de reparto del nodo i en una ronda: u_i(x) = a_i · ln(1 + x), con a_i = coeficiente_utilidad
  - utilidad conjunta: influencia probabilística sobre el grafo (ada/parte2/influencia.py)
  - el grafo es no dirigido y la selección debe cumplir a la vez |S| <= k y Σ costos <= P
"""
from dataclasses import dataclass

from ada.casos import CasoInvalido
from ada.parte2.influencia import matriz_influencia

CAMPOS = {
    "N": "numero_nodos", "T": "numero_rondas", "k": "cupo_participantes_por_ronda_k",
    "B": "presupuesto_ruido_por_ronda_B", "P": "presupuesto_costos_participacion_por_ronda",
}


@dataclass
class CasoRed:
    nombre: str
    ids: list              # id original de cada nodo; internamente el nodo i es ids[i]
    a: list                # coeficiente de utilidad
    W: list                # matriz de influencia N x N (diagonal 1)
    costos: list           # costo de participación
    presupuesto_nodo: list # presupuesto total de ruido de cada nodo para todas las rondas
    T: int
    k: int
    B: int
    P: int

    @property
    def N(self):
        return len(self.ids)


def es_formato_red(datos):
    return isinstance(datos, dict) and "parametros" in datos and "grafo" in datos


def leer_caso_red(datos, nombre="caso"):
    """Valida el diccionario y lo convierte en CasoRed. Costo O(N² + |E|)."""
    p = datos.get("parametros", {})
    valores = {}
    for clave, campo in CAMPOS.items():
        v = p.get(campo)
        if not (isinstance(v, int) and v >= 0):
            raise CasoInvalido(f"parametros.{campo} debe ser un entero >= 0")
        valores[clave] = v
    if valores["k"] < 1 or valores["T"] < 1:
        raise CasoInvalido("k y numero_rondas deben ser >= 1")

    nodos = datos.get("nodos", [])
    if len(nodos) != valores["N"]:
        raise CasoInvalido(f"numero_nodos = {valores['N']} pero hay {len(nodos)} nodos")
    ids = [n.get("id") for n in nodos]
    if None in ids or len(set(ids)) != len(ids):
        raise CasoInvalido("todos los nodos necesitan un 'id' distinto")
    pos = {ident: i for i, ident in enumerate(ids)}
    a, costos, presupuesto_nodo = [], [], []
    for n in nodos:
        coef, costo, tope = n.get("coeficiente_utilidad"), n.get("costo_participacion"), n.get("presupuesto_total_nodo")
        if not (isinstance(coef, (int, float)) and coef > 0):
            raise CasoInvalido(f"nodo {n['id']}: coeficiente_utilidad debe ser > 0")
        if not (isinstance(costo, (int, float)) and costo >= 0):
            raise CasoInvalido(f"nodo {n['id']}: costo_participacion debe ser >= 0")
        if not (isinstance(tope, int) and tope >= 0):
            raise CasoInvalido(f"nodo {n['id']}: presupuesto_total_nodo debe ser un entero >= 0")
        a.append(float(coef))
        costos.append(costo)
        presupuesto_nodo.append(tope)

    aristas = []
    for e in datos.get("grafo", []):
        u, v, w = e.get("u"), e.get("v"), e.get("peso_influencia")
        if u not in pos or v not in pos:
            raise CasoInvalido(f"arista {u}-{v}: nodo desconocido")
        if u == v:
            raise CasoInvalido(f"arista {u}-{v}: no puede unir un nodo consigo mismo")
        if not (isinstance(w, (int, float)) and 0 <= w <= 1):
            raise CasoInvalido(f"arista {u}-{v}: peso_influencia debe estar entre 0 y 1")
        aristas.append((pos[u], pos[v], float(w)))

    return CasoRed(datos.get("nombre", nombre), ids, a, matriz_influencia(len(ids), aristas),
                   costos, presupuesto_nodo, T=valores["T"], k=valores["k"], B=valores["B"], P=valores["P"])
