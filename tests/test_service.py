import tempfile
import unittest
from pathlib import Path

from codigo.service import analizar_fuente


class ServicioAnalisisTest(unittest.TestCase):
    def test_genera_los_reportes_requeridos(self) -> None:
        fuente = 'HORARIO { CURSOS { curso: "X" [codigo: "X-1", creditos: 1], }; };'
        with tempfile.TemporaryDirectory() as temporal:
            resultado = analizar_fuente(fuente, Path(temporal))
            nombres = {ruta.name for ruta in resultado.reportes.values()}
        self.assertEqual(nombres, {"horario_semanal.html", "carga_catedraticos.html", "estadistico_general.html", "errores_lexicos.html", "horario.dot"})


if __name__ == "__main__":
    unittest.main()
