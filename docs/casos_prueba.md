# Casos de prueba

Los casos se ejecutan con `python -m unittest discover -s tests -v` y con el
ejemplo válido de `Proyecto1/ejemplos/`.

| # | Entrada | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| 1 | Archivo válido con cuatro secciones | Tokens válidos y tres reportes | Cumple; 0 errores léxicos |
| 2 | `HORARIO @ CURSOS` | `CARACTER_NO_RECONOCIDO` y continuar | Cumple; llega a `CURSOS` |
| 3 | `inicio: 25:00` | `HORA_FUERA_DE_RANGO` | Cumple |
| 4 | `dia: DOMINGO` | `DIA_NO_RECONOCIDO` | Cumple |
| 5 | Código `LFP-` | `CODIGO_MAL_FORMADO` | Cumple |
| 6 | Cadena sin comilla final | `CADENA_SIN_CERRAR` | Cumple y continúa en la siguiente línea |
| 7 | Dos clases del mismo catedrático, día y traslape | Un choque de catedrático | Cumple |
| 8 | Dos clases del mismo aula, día y traslape | Un choque de aula | Cubierto por `Horario.detectar_choques()` |

El caso válido además verifica las posiciones de línea/columna, comentarios
con caracteres especiales y generación de `horario.dot`.

