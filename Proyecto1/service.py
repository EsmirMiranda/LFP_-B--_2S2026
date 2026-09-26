from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import ErrorLexico
from .lexer import AnalizadorLexico
from .model import Horario
from .parser import AnalizadorHorario, ErrorSintactico
from .reports import GeneradorReportes
from .token import Token


@dataclass
class ResultadoAnalisis:
    tokens: list[Token]
    errores_lexicos: list[ErrorLexico]
    errores_sintacticos: list[ErrorSintactico]
    horario: Horario
    reportes: dict[str, Path]


def analizar_fuente(fuente: str, salida: str | Path) -> ResultadoAnalisis:
    lexer = AnalizadorLexico(fuente)
    tokens = lexer.analizar()
    parser = AnalizadorHorario(tokens)
    horario = parser.analizar()
    reportes = GeneradorReportes(salida).generar_todos(horario, lexer.errores.errores)
    return ResultadoAnalisis(tokens, lexer.errores.errores, parser.errores, horario, reportes)


def analizar_archivo(ruta: str | Path, salida: str | Path) -> ResultadoAnalisis:
    fuente = Path(ruta).read_text(encoding="utf-8")
    return analizar_fuente(fuente, salida)

