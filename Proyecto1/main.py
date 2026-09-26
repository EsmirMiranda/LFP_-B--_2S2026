from __future__ import annotations

import argparse
from pathlib import Path

from .service import analizar_archivo


def ejecutar_cli(ruta: str, salida: str) -> int:
    resultado = analizar_archivo(ruta, salida)
    print(f"Tokens: {len(resultado.tokens) - 1}")
    print(f"Errores léxicos: {len(resultado.errores_lexicos)}")
    print(f"Errores sintácticos: {len(resultado.errores_sintacticos)}")
    print(f"Choques de horario: {len(resultado.horario.choques)}")
    print(f"Reportes generados en: {Path(salida).resolve()}")
    for nombre, archivo in resultado.reportes.items():
        print(f"  - {nombre}: {archivo.name}")
    return 0 if not resultado.errores_lexicos else 1


def main() -> int:
    argumentos = argparse.ArgumentParser(description="Analizador léxico HorarioScript")
    argumentos.add_argument("archivo", nargs="?", help="archivo .hor que se analizará")
    argumentos.add_argument("--salida", default="reportes", help="directorio de reportes")
    argumentos.add_argument("--gui", action="store_true", help="abrir la interfaz Tkinter")
    opciones = argumentos.parse_args()
    if opciones.gui or not opciones.archivo:
        from .gui import iniciar_gui
        iniciar_gui(opciones.archivo)
        return 0
    return ejecutar_cli(opciones.archivo, opciones.salida)


if __name__ == "__main__":
    raise SystemExit(main())

