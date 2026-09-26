# HorarioScript - Proyecto 1 de LFP

Analizador léxico manual para el lenguaje de horarios académicos HorarioScript.
El proyecto implementa un AFD carácter a carácter en Python 3.10+, un parser
tolerante, detección de choques, una interfaz Tkinter y reportes HTML.

## Ejecución

No requiere paquetes externos. Desde la raíz del repositorio:

```powershell
python -m Proyecto1.main Proyecto1/ejemplos/horario_valido.hor --salida reportes
```

La orden genera `horario_semanal.html`, `carga_catedraticos.html`,
`estadistico_general.html`, `errores_lexicos.html` y `horario.dot` dentro de
`reportes/`. Para abrir la GUI:

```powershell
python -m Proyecto1.main --gui
```

También se puede cargar un archivo al iniciar:

```powershell
python -m Proyecto1.main Proyecto1/ejemplos/horario_valido.hor --gui
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Estructura

- `Proyecto1/lexer.py`: AFD manual, tokens, posiciones y recuperación de errores.
- `Proyecto1/parser.py` y `Proyecto1/model.py`: lectura estructural y modelo académico.
- `Proyecto1/reports.py`: los tres reportes requeridos, errores y Graphviz DOT.
- `Proyecto1/gui.py`: interfaz Tkinter con tablas de tokens/errores y accesos a reportes.
- `Proyecto1/ejemplos/`: entradas `.hor` listas para ejecutar.
- `docs/`: manual técnico, manual de usuario y casos de prueba.

La tokenización no usa `re`, `split` ni `find`; las transiciones principales
consumen la entrada con indexación y recorridos carácter a carácter.
