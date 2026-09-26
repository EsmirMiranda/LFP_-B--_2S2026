from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TipoToken(str, Enum):
    HORARIO = "HORARIO"
    CURSOS = "CURSOS"
    CATEDRATICOS = "CATEDRATICOS"
    AULAS = "AULAS"
    CLASES = "CLASES"
    ELEMENTO = "PALABRA_RESERVADA_ELEMENTO"
    RELACION = "PALABRA_RESERVADA_RELACION"
    ATRIBUTO = "ATRIBUTO"
    CODIGO = "CODIGO"
    CADENA = "CADENA"
    HORA = "HORA"
    ENTERO = "ENTERO"
    DIA = "DIA"
    CATEGORIA = "CATEGORIA"
    SIMBOLO = "SIMBOLO"
    COMENTARIO_LINEA = "COMENTARIO_LINEA"
    ERROR_LEXICO = "ERROR_LEXICO"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    numero: int
    lexema: str
    tipo: TipoToken
    linea: int
    columna: int

    def as_dict(self) -> dict[str, object]:
        return {
            "numero": self.numero,
            "lexema": self.lexema,
            "tipo": self.tipo.value,
            "linea": self.linea,
            "columna": self.columna,
        }

