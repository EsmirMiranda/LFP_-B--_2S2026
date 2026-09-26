from __future__ import annotations

from pathlib import Path

from .errors import GestorErrores
from .token import TipoToken, Token


class AnalizadorLexico:
    """AFD manual de HorarioScript, con transiciones carácter a carácter."""

    PALABRAS_BLOQUE = {
        "HORARIO": TipoToken.HORARIO,
        "CURSOS": TipoToken.CURSOS,
        "CATEDRATICOS": TipoToken.CATEDRATICOS,
        "AULAS": TipoToken.AULAS,
        "CLASES": TipoToken.CLASES,
    }
    PALABRAS_ELEMENTO = {"curso", "catedratico", "aula", "clase"}
    PALABRAS_RELACION = {"con", "en"}
    ATRIBUTOS = {
        "codigo", "creditos", "categoria", "capacidad", "edificio",
        "dia", "inicio", "fin", "seccion",
    }
    DIAS = {"LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"}
    CATEGORIAS = {"TITULAR", "INTERINO", "AUXILIAR"}
    SIMBOLOS = set("{}[]:,;")

    def __init__(self, fuente: str) -> None:
        self.fuente = fuente
        self.indice = 0
        self.linea = 1
        self.columna = 1
        self.numero_token = 0
        self.errores = GestorErrores()
        self.atributo_pendiente = ""

    @classmethod
    def desde_archivo(cls, ruta: str | Path) -> "AnalizadorLexico":
        return cls(Path(ruta).read_text(encoding="utf-8"))

    def _actual(self) -> str:
        return self.fuente[self.indice] if self.indice < len(self.fuente) else ""

    def _siguiente(self) -> str:
        posicion = self.indice + 1
        return self.fuente[posicion] if posicion < len(self.fuente) else ""

    def _avanzar(self) -> str:
        caracter = self._actual()
        if caracter == "":
            return caracter
        self.indice += 1
        if caracter == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return caracter

    def _token(self, lexema: str, tipo: TipoToken, linea: int, columna: int) -> Token:
        self.numero_token += 1
        return Token(self.numero_token, lexema, tipo, linea, columna)

    def _error_token(self, lexema: str, tipo: str, descripcion: str, linea: int, columna: int) -> Token:
        self.errores.agregar(lexema, tipo, descripcion, linea, columna)
        return self._token(lexema, TipoToken.ERROR_LEXICO, linea, columna)

    @staticmethod
    def _es_letra(caracter: str) -> bool:
        return ("a" <= caracter <= "z") or ("A" <= caracter <= "Z")

    @staticmethod
    def _es_digito(caracter: str) -> bool:
        return "0" <= caracter <= "9"

    @classmethod
    def _es_alfanumerico(cls, caracter: str) -> bool:
        return cls._es_letra(caracter) or cls._es_digito(caracter)

    def _saltar_blancos(self) -> None:
        while self._actual() in (" ", "\t", "\r", "\n"):
            self._avanzar()

    def _leer_comentario(self, linea: int, columna: int) -> Token:
        inicio = self.indice
        self._avanzar(); self._avanzar()
        while self._actual() not in ("", "\n"):
            self._avanzar()
        return self._token(self.fuente[inicio:self.indice], TipoToken.COMENTARIO_LINEA, linea, columna)

    def _leer_cadena(self, linea: int, columna: int) -> Token:
        inicio = self.indice
        self._avanzar()
        while self._actual() not in ("", "\n", '"'):
            self._avanzar()
        if self._actual() == '"':
            self._avanzar()
            return self._token(self.fuente[inicio:self.indice], TipoToken.CADENA, linea, columna)
        lexema = self.fuente[inicio:self.indice]
        self.errores.agregar(lexema, "CADENA_SIN_CERRAR", f"Cadena sin cerrar iniciada en línea {linea}, columna {columna}", linea, columna)
        return self._token(lexema, TipoToken.ERROR_LEXICO, linea, columna)

    def _leer_numero(self, linea: int, columna: int) -> Token:
        inicio = self.indice
        cantidad = 0
        while self._es_digito(self._actual()):
            cantidad += 1; self._avanzar()
        if cantidad == 2 and self._actual() == ":":
            self._avanzar()
            minutos_inicio = self.indice
            while self._es_digito(self._actual()):
                self._avanzar()
            lexema = self.fuente[inicio:self.indice]
            minutos_texto = self.fuente[minutos_inicio:self.indice]
            hora = int(self.fuente[inicio:inicio + 2])
            valida = len(minutos_texto) == 2
            if valida:
                minutos = int(minutos_texto)
                valida = minutos <= 59 and 6 * 60 <= hora * 60 + minutos <= 21 * 60
            if not valida:
                return self._error_token(lexema, "HORA_FUERA_DE_RANGO", f"Hora fuera de rango en línea {linea}, columna {columna}", linea, columna)
            return self._token(lexema, TipoToken.HORA, linea, columna)
        return self._token(self.fuente[inicio:self.indice], TipoToken.ENTERO, linea, columna)

    def _leer_palabra_o_codigo(self, linea: int, columna: int) -> Token:
        inicio = self.indice
        tiene_letra = False
        while self._es_alfanumerico(self._actual()):
            tiene_letra = tiene_letra or self._es_letra(self._actual())
            self._avanzar()
        hubo_guion = self._actual() == "-"
        digitos = 0
        if hubo_guion:
            self._avanzar()
            while self._es_digito(self._actual()):
                digitos += 1; self._avanzar()
        lexema = self.fuente[inicio:self.indice]
        if hubo_guion:
            if tiene_letra and digitos > 0:
                return self._token(lexema, TipoToken.CODIGO, linea, columna)
            return self._error_token(lexema, "CODIGO_MAL_FORMADO", f"Código mal formado: '{lexema}' en línea {linea}, columna {columna}", linea, columna)
        if self.atributo_pendiente == "dia":
            self.atributo_pendiente = ""
            if lexema in self.DIAS:
                return self._token(lexema, TipoToken.DIA, linea, columna)
            return self._error_token(lexema, "DIA_NO_RECONOCIDO", f"Día no reconocido: '{lexema}' en línea {linea}, columna {columna}", linea, columna)
        if lexema in self.PALABRAS_BLOQUE:
            return self._token(lexema, self.PALABRAS_BLOQUE[lexema], linea, columna)
        if lexema in self.PALABRAS_ELEMENTO:
            return self._token(lexema, TipoToken.ELEMENTO, linea, columna)
        if lexema in self.PALABRAS_RELACION:
            return self._token(lexema, TipoToken.RELACION, linea, columna)
        if lexema in self.ATRIBUTOS:
            self.atributo_pendiente = lexema
            return self._token(lexema, TipoToken.ATRIBUTO, linea, columna)
        if lexema in self.DIAS:
            return self._token(lexema, TipoToken.DIA, linea, columna)
        if lexema in self.CATEGORIAS:
            return self._token(lexema, TipoToken.CATEGORIA, linea, columna)
        return self._error_token(lexema, "CODIGO_MAL_FORMADO", f"Código mal formado: '{lexema}' en línea {linea}, columna {columna}", linea, columna)

    def siguiente_token(self) -> Token:
        self._saltar_blancos()
        linea, columna, actual = self.linea, self.columna, self._actual()
        if actual == "":
            return self._token("", TipoToken.EOF, linea, columna)
        if actual == "#" and self._siguiente() == "#":
            return self._leer_comentario(linea, columna)
        if actual == '"':
            return self._leer_cadena(linea, columna)
        if actual in self.SIMBOLOS:
            self._avanzar(); return self._token(actual, TipoToken.SIMBOLO, linea, columna)
        if self._es_digito(actual):
            return self._leer_numero(linea, columna)
        if self._es_letra(actual):
            return self._leer_palabra_o_codigo(linea, columna)
        self._avanzar()
        return self._error_token(actual, "CARACTER_NO_RECONOCIDO", f"Carácter no reconocido: '{actual}' en línea {linea}, columna {columna}", linea, columna)

    def analizar(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            token = self.siguiente_token(); tokens.append(token)
            if token.tipo is TipoToken.EOF:
                return tokens
