# Guion para la sustentación grupal

Plan para una exposición de **18 minutos**. Los nombres quedan como campos editables hasta confirmar quiénes integran el equipo. La presentación que acompaña este guion contiene las diapositivas en el mismo orden.

## Reparto y tiempos

| Tiempo | Diapositiva | Ponente | Qué explicar |
|---|---|---|---|
| 0:00–0:30 | Portada | [Nombre A] | Presentar el proyecto y anticipar las dos decisiones: selección de nodos y reparto de ruido. |
| 0:30–2:00 | Dos decisiones por ronda | [Nombre A] | Definir T, k, B, costos y saldos; explicar qué observa V2 cuando empieza cada ronda. |
| 2:00–4:00 | Reparto voraz óptimo | [Nombre B] | Mostrar ganancias marginales decrecientes y el intercambio que justifica escoger las B mayores. Cerrar con O(n+B log n). |
| 4:00–6:00 | Reducción desde Cobertura Máxima | [Nombre B] | Dar el problema de origen, la transformación, ambas direcciones y por qué la reducción debe ir hacia selección. |
| 6:00–7:30 | Exacto frente a voraz | [Nombre C] | Contrastar fuerza bruta y selección voraz; explicar por qué el exacto es útil como referencia en instancias pequeñas. |
| 7:30–9:30 | Garantía (1−1/e) | [Nombre C] | Explicar la brecha respecto del óptimo y la recurrencia; precisar que la prueba básica supone cardinalidad, no presupuesto de costos. |
| 9:30–11:00 | Variantes | [Nombre C] | Resumir costos, algoritmo exacto de referencia y el alcance limitado de la garantía V2; decir que V3 sigue pendiente. |
| 11:00–12:30 | Tiempos V2 | [Nombre D] | Describir las dos barridas, mediana de cinco ejecuciones, variables fijas y qué incluye el cronómetro. |
| 12:30–14:00 | Calidad ante fallas | [Nombre D] | Leer la comparación con óptimo factible y explicar los resultados para distintos niveles de fallas sin generalizar más allá de los casos medidos. |
| 14:00–17:00 | Demostración | [Nombre D] | Ejecutar el flujo reproducible de abajo. |
| 17:00–18:00 | Preguntas y cierre | Todas las personas | Responder en una frase y ampliar solo si se solicita; cerrar con el estado verificable del proyecto. |

Si son menos de cuatro integrantes, combinar bloques contiguos. Si son más, dividir reducción, análisis experimental o demostración. Sustituir [Nombre A–D] por nombres reales y ajustar las transiciones antes del ensayo.

## Guion de la demostración (3 minutos)

1. **0:00–0:30 — Abrir el modo demo.** Tener la aplicación iniciada con `streamlit run app/principal.py`. Explicar que el escenario base permite recorrer la selección paso a paso.
2. **0:30–1:15 — Mostrar selección y reparto.** Avanzar una ronda; señalar las ganancias marginales/candidatos elegidos y después el reparto de unidades de ruido entre los nodos seleccionados.
3. **1:15–2:15 — Activar V2.** Usar la probabilidad de fallas `p=0.2` y la semilla fija `7`. Indicar qué nodos están disponibles al inicio de la ronda, ejecutar y comparar la selección con el escenario base.
4. **2:15–2:45 — Revisar resultados.** Mostrar la traza por ronda, el reparto y las verificaciones visibles. Aclarar que la semilla hace reproducible este ejemplo; no significa que el mismo resultado describa todas las realizaciones aleatorias.
5. **2:45–3:00 — Cerrar.** Volver a la diapositiva de preguntas. Si falla la interfaz, explicar el caso con las capturas/evidencias V2 del repositorio y seguir con las preguntas.

### Preparación antes de presentar

- Iniciar la aplicación y abrir el modo demo antes de compartir pantalla.
- Confirmar que el control V2 está visible, fijar `p=0.2` y semilla `7`, y comprobar que la corrida termina.
- Tener listo el escenario base para la comparación y las diapositivas de respaldo si la interfaz no carga.
- No prometer resultados de V3: sus supuestos y experimentos siguen pendientes de confirmación.

## Preguntas y respuestas breves

**¿Por qué el reparto voraz es óptimo?** Las ganancias marginales no aumentan por concavidad. Escoger repetidamente la mayor disponible equivale a tomar las B mayores; el intercambio no reduce el valor y mantiene prefijos factibles.

**¿Qué significa pseudo-polinomial?** El número de operaciones depende del valor numérico de B. En una codificación binaria, ese valor puede ser exponencial en la longitud de la entrada, aunque el algoritmo de reparto sea exacto.

**¿Qué prueba la reducción?** Una solución de Cobertura Máxima se transforma en una selección con el mismo valor y viceversa. Por tanto, un algoritmo polinomial exacto para selección daría uno para Cobertura Máxima.

**¿Por qué el voraz de selección da (1−1/e)?** Con función monótona submodular y solo una restricción de cardinalidad, cada paso reduce la brecha al óptimo al menos en una fracción 1/k. Con costos, esta demostración por sí sola no aplica.

**¿Qué garantía se afirma para V2?** La cota por ronda se refiere al óptimo factible del estado observado bajo las condiciones indicadas en la guía. No se afirma una garantía global frente a la política dinámica óptima de todas las rondas.

**¿Qué pasa con V3?** Está pendiente confirmar sus supuestos y resultados con el equipo docente. No se presenta como funcionalidad o resultado validado.

## Ensayo del equipo

Hacer un ensayo con cronómetro y usar los 18 minutos como límite. Cada integrante debe poder explicar sin notas la reducción desde Cobertura Máxima y la complejidad del algoritmo exacto. En el repaso cruzado, otra persona hace dos preguntas de la guía de estudio; quien expone responde y apunta qué explicación necesita ajuste. Registrar quién controla la demo y quién toma el relevo si falla.

**Pendiente para cerrar la preparación:** completar los nombres reales y realizar el ensayo cronometrado del equipo. Este guion deja la estructura lista, pero no afirma que el ensayo ya haya ocurrido.
