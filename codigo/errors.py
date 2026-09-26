from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorLexico:
    numero: int
    lexema: str
    tipo: str
    descripcion: str
    linea: int
    columna: int

    def as_dict(self) -> dict[str, object]:
        return {
            "numero": self.numero,
            "lexema": self.lexema,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "linea": self.linea,
            "columna": self.columna,
        }


class GestorErrores:
    """Acumula errores sin interrumpir el recorrido del archivo."""

    def __init__(self) -> None:
        self.errores: list[ErrorLexico] = []

    def agregar(
        self,
        lexema: str,
        tipo: str,
        descripcion: str,
        linea: int,
        columna: int,
    ) -> ErrorLexico:
        error = ErrorLexico(
            len(self.errores) + 1,
            lexema,
            tipo,
            descripcion,
            linea,
            columna,
        )
        self.errores.append(error)
        return error

