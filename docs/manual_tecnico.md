# Manual técnico

## Arquitectura

El sistema está organizado en cinco capas:

1. `AnalizadorLexico` recorre la fuente con un índice, línea y columna. Cada
   estado de lectura se expresa con funciones de transición para blancos,
   comentarios, cadenas, números, palabras/códigos y símbolos.
2. `Token` conserva número, lexema, tipo y posición. `GestorErrores` acumula
   errores sin detener el análisis.
3. `AnalizadorHorario` consume tokens válidos y construye `Horario`, `Curso`,
   `Catedratico`, `Aula` y `Clase`.
4. `Horario.detectar_choques()` compara pares de clases del mismo día. Hay
   traslape si `inicio_a < fin_b` y `inicio_b < fin_a`; se reporta por
   catedrático y por aula de forma independiente.
5. `GeneradorReportes` transforma el modelo en HTML con CSS embebido y genera
   un grafo DOT de las relaciones.

## AFD y prioridades

El estado inicial ignora espacios y actualiza la posición. `##` conduce al
estado de comentario hasta salto de línea o EOF. `"` conduce al estado de
cadena; salto de línea/EOF sin otra comilla produce `CADENA_SIN_CERRAR`.

Una secuencia numérica de dos dígitos seguida de `:` se evalúa como hora y se
valida entre 06:00 y 21:00. Las demás secuencias numéricas son `ENTERO`.
Una palabra se compara con las tablas de reservadas; si contiene guion se
valida como código alfanumérico seguido de guion y dígitos. La lista de días y
categorías tiene prioridad sobre la clasificación genérica.

## Recuperación

Los errores léxicos generan un token `ERROR_LEXICO`, se registran con posición
exacta y el índice avanza. Así el analizador continúa y el HTML
`errores_lexicos.html` presenta todos los problemas de una pasada.

## Reportes

- `horario_semanal.html`: clases agrupadas por sección y estado confirmado o
  choque.
- `carga_catedraticos.html`: horas, cursos, secciones y nivel de carga.
- `estadistico_general.html`: KPIs, promedio y ocupación estimada de aulas.
- `horario.dot`: jerarquía de horario, secciones y relaciones con clases.

