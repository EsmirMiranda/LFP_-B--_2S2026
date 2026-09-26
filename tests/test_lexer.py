import unittest

from Proyecto1.lexer import AnalizadorLexico
from Proyecto1.token import TipoToken


class AnalizadorLexicoTest(unittest.TestCase):
    def test_reconoce_tokens_y_posiciones(self) -> None:
        fuente = 'HORARIO { dia: MARTES, inicio: 07:00, codigo: "LFP-0796" };'
        lexer = AnalizadorLexico(fuente)
        tokens = lexer.analizar()
        tipos = [token.tipo for token in tokens]
        self.assertEqual(tipos[:6], [TipoToken.HORARIO, TipoToken.SIMBOLO, TipoToken.ATRIBUTO, TipoToken.SIMBOLO, TipoToken.DIA, TipoToken.SIMBOLO])
        self.assertEqual(tokens[0].linea, 1)
        self.assertEqual(tokens[0].columna, 1)
        self.assertEqual(tokens[8].tipo, TipoToken.HORA)
        self.assertEqual(tokens[8].lexema, "07:00")
        self.assertEqual(tokens[-1].tipo, TipoToken.EOF)

    def test_comentario_es_un_token_y_no_genera_error(self) -> None:
        lexer = AnalizadorLexico("## @ % comentario\nHORARIO")
        tokens = lexer.analizar()
        self.assertEqual(tokens[0].tipo, TipoToken.COMENTARIO_LINEA)
        self.assertEqual(len(lexer.errores.errores), 0)

    def test_acumula_errores_y_continua(self) -> None:
        lexer = AnalizadorLexico('HORARIO @ 25:00 "sin cierre\nCURSOS')
        tokens = lexer.analizar()
        tipos_error = [error.tipo for error in lexer.errores.errores]
        self.assertIn("CARACTER_NO_RECONOCIDO", tipos_error)
        self.assertIn("HORA_FUERA_DE_RANGO", tipos_error)
        self.assertIn("CADENA_SIN_CERRAR", tipos_error)
        self.assertEqual(tokens[-2].tipo, TipoToken.CURSOS)
        self.assertEqual(tokens[-1].tipo, TipoToken.EOF)

    def test_reporta_dia_no_reconocido_en_el_atributo_dia(self) -> None:
        lexer = AnalizadorLexico("dia: DOMINGO")
        lexer.analizar()
        self.assertEqual(lexer.errores.errores[0].tipo, "DIA_NO_RECONOCIDO")


if __name__ == "__main__":
    unittest.main()
