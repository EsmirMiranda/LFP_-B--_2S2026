# Manual de usuario

## 1. Preparar un archivo

Use la extensión `.hor` y la estructura raíz `HORARIO` con las secciones
`CURSOS`, `CATEDRATICOS`, `AULAS` y `CLASES`. El ejemplo completo está en
`doc de prueba/conjunto1_valido_base.hor`.

## 2. Ejecutar por consola

Desde la raíz del repositorio:

```powershell
python -m codigo.main "doc de prueba/conjunto1_valido_base.hor" --salida reportes
```

La consola informa cantidad de tokens, errores y choques. Abra los HTML del
directorio indicado en cualquier navegador.

## 3. Ejecutar con Tkinter

Use `python -m codigo.main --gui`, presione **Cargar .hor**, seleccione el
archivo y presione **Analizar**. La pestaña **Tokens** muestra número, lexema,
tipo, línea y columna. **Errores léxicos** muestra el tipo, descripción y
posición. En **Reportes** se abren los HTML y el archivo DOT generado.

## 4. Interpretar resultados

Una fila verde significa `CONFIRMADO`. Una fila roja significa
`CHOQUE DE HORARIO`: el mismo catedrático o aula aparece en clases traslapadas
del mismo día. Las horas deben estar entre 06:00 y 21:00.
