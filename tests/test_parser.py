import unittest

from codigo.parser import AnalizadorHorario


FUENTE = '''HORARIO {
CURSOS { curso: "Lenguajes Formales" [codigo: "LFP-0796", creditos: 4], };
CATEDRATICOS { catedratico: "Otto Rodriguez" [codigo: "DOC-001", categoria: TITULAR], };
AULAS { aula: "A-101" [capacidad: 40, edificio: "T-3"], };
CLASES {
clase: "LFP-0796" con "DOC-001" en "A-101" [dia: LUNES, inicio: 07:00, fin: 08:40, seccion: "N"],
clase: "LFP-0796" con "DOC-001" en "A-102" [dia: LUNES, inicio: 08:00, fin: 09:00, seccion: "A"],
};
};'''


class AnalizadorHorarioTest(unittest.TestCase):
    def test_construye_entidades_y_detecta_choque(self) -> None:
        parser, lexer = AnalizadorHorario.desde_fuente(FUENTE)
        horario = parser.analizar()
        self.assertEqual(len(lexer.errores.errores), 0)
        self.assertEqual(len(parser.errores), 0)
        self.assertEqual(len(horario.cursos), 1)
        self.assertEqual(len(horario.clases), 2)
        self.assertEqual(len(horario.choques), 1)
        self.assertEqual(horario.choques[0].recurso, "CATEDRATICO")

    def test_error_lexico_en_atributo_no_desplaza_los_valores_siguientes(self) -> None:
        fuente = '''HORARIO {
CLASES {
clase: "LFP-0796" con "DOC-001" en "A-101" [dia: FERIADO, inicio: 13:00, fin: 14:40, seccion: "A"],
};
};'''
        parser, lexer = AnalizadorHorario.desde_fuente(fuente)
        horario = parser.analizar()
        self.assertEqual(len(lexer.errores.errores), 1)
        self.assertEqual(horario.clases[0].dia, "")
        self.assertEqual(horario.clases[0].inicio, "13:00")
        self.assertEqual(horario.clases[0].fin, "14:40")


if __name__ == "__main__":
    unittest.main()
