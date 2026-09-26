from __future__ import annotations

from dataclasses import dataclass

from .lexer import AnalizadorLexico
from .model import Aula, Catedratico, Clase, Curso, Horario, quitar_comillas
from .token import TipoToken, Token


@dataclass(frozen=True)
class ErrorSintactico:
    descripcion: str
    linea: int
    columna: int


class AnalizadorHorario:
    """Parser tolerante para construir el modelo desde los tokens del AFD."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.indice = 0
        self.errores: list[ErrorSintactico] = []

    @classmethod
    def desde_fuente(cls, fuente: str) -> tuple["AnalizadorHorario", AnalizadorLexico]:
        lexer = AnalizadorLexico(fuente)
        return cls(lexer.analizar()), lexer

    def _actual(self) -> Token:
        return self.tokens[self.indice]

    def _avanzar(self) -> Token:
        token = self._actual()
        if self.indice < len(self.tokens) - 1:
            self.indice += 1
        return token

    def _limpiar(self) -> None:
        while self._actual().tipo in (TipoToken.COMENTARIO_LINEA, TipoToken.ERROR_LEXICO):
            self._avanzar()

    def _es(self, tipo: TipoToken | None = None, lexema: str | None = None) -> bool:
        self._limpiar()
        token = self._actual()
        return (tipo is None or token.tipo is tipo) and (lexema is None or token.lexema == lexema)

    def _aceptar(self, tipo: TipoToken | None = None, lexema: str | None = None) -> Token | None:
        if self._es(tipo, lexema):
            return self._avanzar()
        return None

    def _requerir(self, tipo: TipoToken | None = None, lexema: str | None = None) -> Token | None:
        token = self._aceptar(tipo, lexema)
        if token is not None:
            return token
        actual = self._actual()
        esperado = lexema or (tipo.value if tipo else "token")
        self.errores.append(ErrorSintactico(f"Se esperaba {esperado} y se encontró '{actual.lexema}'", actual.linea, actual.columna))
        return None

    def _valor(self) -> str:
        self._limpiar()
        token = self._actual()
        if token.tipo is TipoToken.EOF:
            return ""
        self._avanzar()
        return quitar_comillas(token.lexema)

    def _atributos(self) -> dict[str, str]:
        valores: dict[str, str] = {}
        if self._aceptar(TipoToken.SIMBOLO, "[") is None:
            return valores
        while not self._es(TipoToken.EOF) and not self._es(TipoToken.SIMBOLO, "]"):
            atributo = self._aceptar(TipoToken.ATRIBUTO)
            if atributo is None:
                self._avanzar()
                continue
            self._aceptar(TipoToken.SIMBOLO, ":")
            valores[atributo.lexema] = self._valor()
            self._aceptar(TipoToken.SIMBOLO, ",")
        self._aceptar(TipoToken.SIMBOLO, "]")
        return valores

    def _separador(self) -> None:
        self._aceptar(TipoToken.SIMBOLO, ",")
        self._aceptar(TipoToken.SIMBOLO, ";")

    def _curso(self, horario: Horario) -> None:
        self._avanzar()
        self._aceptar(TipoToken.SIMBOLO, ":")
        nombre = self._valor()
        atributos = self._atributos()
        try:
            horario.cursos.append(Curso(nombre, atributos.get("codigo", ""), int(atributos.get("creditos", 0))))
        except ValueError:
            horario.cursos.append(Curso(nombre, atributos.get("codigo", ""), 0))
        self._separador()

    def _catedratico(self, horario: Horario) -> None:
        self._avanzar()
        self._aceptar(TipoToken.SIMBOLO, ":")
        nombre = self._valor()
        atributos = self._atributos()
        horario.catedraticos.append(Catedratico(nombre, atributos.get("codigo", ""), atributos.get("categoria", "")))
        self._separador()

    def _aula(self, horario: Horario) -> None:
        self._avanzar()
        self._aceptar(TipoToken.SIMBOLO, ":")
        codigo = self._valor()
        atributos = self._atributos()
        try:
            capacidad = int(atributos.get("capacidad", 0))
        except ValueError:
            capacidad = 0
        horario.aulas.append(Aula(codigo, capacidad, atributos.get("edificio", "")))
        self._separador()

    def _clase(self, horario: Horario) -> None:
        self._avanzar()
        self._aceptar(TipoToken.SIMBOLO, ":")
        curso = self._valor()
        self._aceptar(TipoToken.RELACION, "con")
        catedratico = self._valor()
        self._aceptar(TipoToken.RELACION, "en")
        aula = self._valor()
        atributos = self._atributos()
        horario.clases.append(Clase(curso, catedratico, aula, atributos.get("dia", ""), atributos.get("inicio", ""), atributos.get("fin", ""), atributos.get("seccion", "")))
        self._separador()

    def _seccion(self, tipo: TipoToken, elemento: TipoToken, metodo) -> None:
        if self._aceptar(tipo) is None:
            return
        self._requerir(TipoToken.SIMBOLO, "{")
        while not self._es(TipoToken.EOF) and not self._es(TipoToken.SIMBOLO, "}"):
            if self._es(elemento):
                metodo()
            else:
                self._avanzar()
        self._aceptar(TipoToken.SIMBOLO, "}")

    def analizar(self) -> Horario:
        horario = Horario()
        self._aceptar(TipoToken.HORARIO)
        self._aceptar(TipoToken.SIMBOLO, "{")
        while not self._es(TipoToken.EOF) and not self._es(TipoToken.SIMBOLO, "}"):
            if self._es(TipoToken.CURSOS):
                self._seccion(TipoToken.CURSOS, TipoToken.ELEMENTO, lambda: self._curso(horario))
            elif self._es(TipoToken.CATEDRATICOS):
                self._seccion(TipoToken.CATEDRATICOS, TipoToken.ELEMENTO, lambda: self._catedratico(horario))
            elif self._es(TipoToken.AULAS):
                self._seccion(TipoToken.AULAS, TipoToken.ELEMENTO, lambda: self._aula(horario))
            elif self._es(TipoToken.CLASES):
                self._seccion(TipoToken.CLASES, TipoToken.ELEMENTO, lambda: self._clase(horario))
            else:
                self._avanzar()
        self._aceptar(TipoToken.SIMBOLO, "}")
        horario.detectar_choques()
        return horario

