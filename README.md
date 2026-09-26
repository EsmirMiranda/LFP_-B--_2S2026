# HorarioScript - Proyecto 1 de LFP

Analizador léxico manual para el lenguaje de horarios académicos HorarioScript.
El proyecto implementa un AFD carácter a carácter en Python 3.10+, un parser
tolerante, detección de choques, una interfaz Tkinter y reportes HTML.

## Ejecución

No requiere paquetes externos. Desde la raíz del repositorio:

```powershell
python -m codigo.main "doc de prueba/conjunto1_valido_base.hor" --salida reportes
```

La orden genera `horario_semanal.html`, `carga_catedraticos.html`,
`estadistico_general.html`, `errores_lexicos.html` y `horario.dot` dentro de
`reportes/`. Para abrir la GUI:

```powershell
python -m codigo.main --gui
```

También se puede cargar un archivo al iniciar:

```powershell
python -m codigo.main "doc de prueba/conjunto1_valido_base.hor" --gui
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Estructura

- `codigo/lexer.py`: AFD manual, tokens, posiciones y recuperación de errores.
- `codigo/parser.py` y `codigo/model.py`: lectura estructural y modelo académico.
- `codigo/reports.py`: los reportes requeridos, errores y Graphviz DOT.
- `codigo/gui.py`: interfaz Tkinter con tablas de tokens/errores y accesos a reportes.
- `doc de prueba/`: entradas `.hor` listas para ejecutar.
- `docs/`: manual técnico, manual de usuario y casos de prueba.

La tokenización no usa `re`, `split` ni `find`; las transiciones principales
consumen la entrada con indexación y recorridos carácter a carácter.
