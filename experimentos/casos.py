"""
Ejecuta casos de prueba con la solución base y guarda la evidencia de cada uno:
resultado, tiempo, traza de la selección, traza del reparto y verificación de restricciones.

Uso:
    python -m experimentos.casos                      # todos los casos de casos/ejemplos/
    python -m experimentos.casos casos/profesora/     # una carpeta con archivos .json
    python -m experimentos.casos caso_01.json caso_02.json
    python -m experimentos.casos --generar-ejemplos   # vuelve a crear casos/ejemplos/

Salida en resultados/casos/<nombre>/:
    resultado.json, traza_seleccion.csv, traza_reparto.csv (si B no es muy grande), reparto.csv
    y, en los casos de la profesora, verificacion.csv. Los CSV llevan una columna "ronda".
Además, un resumen de todos los casos en resultados/casos/resumen.csv.
"""
import argparse
import glob
import json
import os

from ada.casos import caso_sintetico, leer_caso, optimo_si_es_factible, resultado_a_dict
from ada.casos_red import es_formato_red, leer_caso_red
from ada.ronda import resolver_ronda
from ada.solucion_red import resolver_caso_red
from experimentos.comun import RAIZ, carpeta_salida, guardar_csv

CARPETA_EJEMPLOS = os.path.join(RAIZ, "casos", "ejemplos")

EJEMPLOS = [  # nombre, N, M, d, k, B, semilla
    ("caso_01_pequeno", 12, 24, 5, 4, 20, 2),
    ("caso_02_mediano", 200, 400, 12, 10, 500, 1),
    ("caso_03_grande", 2000, 2000, 20, 20, 5000, 3),
]


def generar_ejemplos():
    os.makedirs(CARPETA_EJEMPLOS, exist_ok=True)
    for nombre, N, M, d, k, B, semilla in EJEMPLOS:
        caso = caso_sintetico(nombre, N, M, d, k, B, semilla)
        _escribir_json(os.path.join(CARPETA_EJEMPLOS, f"{nombre}.json"), caso)
    # un caso con utilidades dadas como tabla, para mostrar ese formato
    tabla = caso_sintetico("caso_04_tablas", 8, 16, 4, 3, 12, 5)
    for i, nodo in enumerate(tabla["nodos"]):
        a = 2 + i
        nodo["utilidad"] = {"familia": "tabla", "valores": [round(a * (1 - 0.7 ** x), 4) for x in range(13)]}
    _escribir_json(os.path.join(CARPETA_EJEMPLOS, "caso_04_tablas.json"), tabla)
    print(f"Ejemplos creados en {CARPETA_EJEMPLOS}")


def ejecutar_caso(datos, con_optimo=True):
    """
    Resuelve un caso (diccionario) y devuelve el resultado serializable.
    Reconoce los dos formatos: el de la profesora (con "parametros" y "grafo") y el provisional.
    """
    if es_formato_red(datos):
        return resolver_caso_red(leer_caso_red(datos, datos.get("nombre", "caso")), con_optimo)
    caso = leer_caso(datos)
    r = resolver_ronda(caso.conjuntos, caso.pesos, caso.k, caso.utilidades, caso.B)
    optimo = optimo_si_es_factible(caso) if con_optimo else None
    return resultado_a_dict(caso, r, optimo)


def guardar_evidencia(datos, res, salida):
    """Escribe resultado.json (con el caso de entrada incluido) y las trazas en CSV."""
    os.makedirs(salida, exist_ok=True)
    _escribir_json(os.path.join(salida, "resultado.json"), {"entrada": datos, "resultado": res})
    rondas = res["rondas"] if res.get("formato") == "red" else [res]
    con_ronda = lambda clave: [{"ronda": r.get("ronda", 1), **fila} for r in rondas for fila in r[clave]]
    guardar_csv(os.path.join(salida, "traza_seleccion.csv"), con_ronda("traza_seleccion"))
    if any(r["traza_reparto"] for r in rondas):
        guardar_csv(os.path.join(salida, "traza_reparto.csv"), con_ronda("traza_reparto"))
    guardar_csv(os.path.join(salida, "reparto.csv"), con_ronda("reparto"))
    if res.get("formato") == "red":
        guardar_csv(os.path.join(salida, "verificacion.csv"),
                    [*[v for r in rondas for v in r["verificaciones"]], *res["verificacion_global"]])


def fila_resumen(res):
    """Una fila por caso, con las mismas columnas para los dos formatos (en red se suman las rondas)."""
    rondas = res["rondas"] if res.get("formato") == "red" else [res]
    optimos = [r["optimo"]["valor"] for r in rondas if r["optimo"]]
    suma = lambda clave: sum(r["tiempo_s"][clave] for r in rondas) * 1e3
    return {"caso": res["caso"], "rondas": len(rondas), "N": res["N"], "k": res["k"], "B": res["B"],
            "f(S)": round(sum(r["utilidad_conjunta"] for r in rondas), 4),
            "optimo_f": round(sum(optimos), 4) if len(optimos) == len(rondas) else "",
            "U(x)": round(sum(r["utilidad_reparto"] for r in rondas), 4),
            "t_seleccion_ms": round(suma("seleccion"), 4), "t_reparto_ms": round(suma("reparto"), 4),
            "t_total_ms": round(suma("total"), 4), "cumple_restricciones": res["cumple_todo"]}


def _escribir_json(ruta, obj):
    """Con sangría si es pequeño (se lee a mano); compacto si es grande."""
    texto = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if len(texto) < 50_000:
        texto = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(texto)


def actualizar_resumen(base):
    """Rehace resumen.csv con todos los casos guardados en base/, no solo los de esta ejecución."""
    filas = []
    for ruta in sorted(glob.glob(os.path.join(base, "*", "resultado.json"))):
        with open(ruta, encoding="utf-8") as fh:
            filas.append(fila_resumen(json.load(fh)["resultado"]))
    if filas:
        guardar_csv(os.path.join(base, "resumen.csv"), filas)
    return len(filas)


def _archivos(rutas):
    archivos = []
    for r in rutas:
        archivos += sorted(glob.glob(os.path.join(r, "*.json"))) if os.path.isdir(r) else [r]
    return archivos


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ejecuta casos con la solución base y guarda la evidencia.")
    p.add_argument("rutas", nargs="*", default=[CARPETA_EJEMPLOS], help="archivos .json o carpetas")
    p.add_argument("--sin-optimo", action="store_true", help="no calcular el óptimo por fuerza bruta")
    p.add_argument("--generar-ejemplos", action="store_true", help="crear los casos de casos/ejemplos/")
    a = p.parse_args()
    if a.generar_ejemplos:
        generar_ejemplos()
    else:
        base = carpeta_salida("casos")
        filas = []
        for archivo in _archivos(a.rutas):
            with open(archivo, encoding="utf-8") as fh:
                datos = json.load(fh)
            datos.setdefault("nombre", os.path.splitext(os.path.basename(archivo))[0])
            res = ejecutar_caso(datos, con_optimo=not a.sin_optimo)
            guardar_evidencia(datos, res, os.path.join(base, res["caso"]))
            filas.append(fila_resumen(res))
            f = filas[-1]
            print(f"  {f['caso']:<18} N={f['N']:>5} k={f['k']:>3} B={f['B']:>6}  f(S)={f['f(S)']:>10.3f}  "
                  f"U(x)={f['U(x)']:>9.3f}  t={f['t_total_ms']:>9.3f} ms  "
                  f"{'cumple' if f['cumple_restricciones'] else 'NO CUMPLE'}")
        if filas:
            todas = actualizar_resumen(base)
            print(f"\nEvidencia de {len(filas)} casos en {base} (resumen.csv con {todas} casos guardados)")
