from __future__ import annotations

from html import escape
from pathlib import Path

from .errors import ErrorLexico
from .model import Choque, Horario


ESTILOS = """
body { font-family: Arial, sans-serif; margin: 2rem; color: #17202a; background: #f6f8fa; }
h1, h2 { color: #12355b; }
.card { background: white; border-radius: 10px; padding: 1rem; margin: 1rem 0; box-shadow: 0 2px 8px #0001; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; background: white; }
th, td { border: 1px solid #d8dee4; padding: .55rem; text-align: left; vertical-align: top; }
th { background: #12355b; color: white; }
.confirmado { background: #d9f7df; }
.choque { background: #ffd6d6; color: #8a1010; font-weight: bold; }
.baja { color: #1261a0; } .normal { color: #16803c; } .alta { color: #b45309; } .saturada { color: #b91c1c; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.kpi { padding: 1rem; border-left: 5px solid #2f81f7; background: white; }
.kpi strong { display: block; font-size: 1.8rem; }
.bar { background: #e5e7eb; border-radius: 6px; overflow: hidden; height: 1.1rem; }
.bar span { display: block; height: 100%; background: #2f81f7; }
"""


def _pagina(titulo: str, contenido: str) -> str:
    return f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{escape(titulo)}</title><style>{ESTILOS}</style></head><body><h1>{escape(titulo)}</h1>{contenido}</body></html>"


class GeneradorReportes:
    def __init__(self, salida: str | Path) -> None:
        self.salida = Path(salida)
        self.salida.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _clase_choque(clase, choques: list[Choque]) -> bool:
        return any(choque.primera is clase or choque.segunda is clase for choque in choques)

    def generar_horario_semanal(self, horario: Horario) -> Path:
        filas: list[str] = []
        por_seccion: dict[str, list] = {}
        for clase in horario.clases:
            por_seccion.setdefault(clase.seccion or "SIN_SECCION", []).append(clase)
        for seccion, clases in sorted(por_seccion.items()):
            filas.append(f"<div class='card'><h2>Sección {escape(seccion)}</h2><table><tr><th>Día</th><th>Horario</th><th>Curso</th><th>Catedrático</th><th>Aula</th><th>Estado</th></tr>")
            for clase in sorted(clases, key=lambda item: (item.dia, item.inicio, item.curso)):
                en_choque = self._clase_choque(clase, horario.choques)
                estado = "CHOQUE DE HORARIO" if en_choque else "CONFIRMADO"
                clase_css = "choque" if en_choque else "confirmado"
                filas.append(f"<tr class='{clase_css}'><td>{escape(clase.dia)}</td><td>{escape(clase.inicio)} - {escape(clase.fin)}</td><td>{escape(clase.curso)}</td><td>{escape(clase.catedratico)}</td><td>{escape(clase.aula)}</td><td>{estado}</td></tr>")
            filas.append("</table></div>")
        if not filas:
            filas.append("<div class='card'>No hay clases programadas.</div>")
        destino = self.salida / "horario_semanal.html"
        destino.write_text(_pagina("Horario semanal por sección", "".join(filas)), encoding="utf-8")
        return destino

    def generar_carga_catedraticos(self, horario: Horario) -> Path:
        filas = ["<table><tr><th>Nombre</th><th>Código</th><th>Categoría</th><th>Horas</th><th>Cursos</th><th>Secciones</th><th>Nivel</th></tr>"]
        for catedratico in horario.catedraticos:
            clases = [clase for clase in horario.clases if clase.catedratico == catedratico.codigo]
            horas = sum(clase.duracion_horas for clase in clases)
            cursos = {clase.curso for clase in clases}
            secciones = {clase.seccion for clase in clases}
            if horas <= 4:
                nivel, css = "BAJA", "baja"
            elif horas <= 10:
                nivel, css = "NORMAL", "normal"
            elif horas <= 15:
                nivel, css = "ALTA", "alta"
            else:
                nivel, css = "SATURADA", "saturada"
            filas.append(f"<tr><td>{escape(catedratico.nombre)}</td><td>{escape(catedratico.codigo)}</td><td>{escape(catedratico.categoria)}</td><td>{horas:.2f}</td><td>{len(cursos)}</td><td>{len(secciones)}</td><td class='{css}'>{nivel}</td></tr>")
        filas.append("</table>")
        destino = self.salida / "carga_catedraticos.html"
        destino.write_text(_pagina("Carga de catedráticos", "".join(filas)), encoding="utf-8")
        return destino

    def generar_estadistico(self, horario: Horario) -> Path:
        horas = {catedratico.codigo: sum(clase.duracion_horas for clase in horario.clases if clase.catedratico == catedratico.codigo) for catedratico in horario.catedraticos}
        ocupacion = {aula.codigo: sum(1 for clase in horario.clases if clase.aula == aula.codigo) for aula in horario.aulas}
        mayor_catedratico = max(horas, key=horas.get, default="N/D")
        mayor_aula = max(ocupacion, key=ocupacion.get, default="N/D")
        promedio = sum(horas.values()) / len(horas) if horas else 0
        indicadores = [("Cursos", len(horario.cursos)), ("Catedráticos", len(horario.catedraticos)), ("Aulas", len(horario.aulas)), ("Clases", len(horario.clases)), ("Choques", len(horario.choques))]
        contenido = ["<div class='kpis'>"]
        for titulo, valor in indicadores:
            contenido.append(f"<div class='kpi'><span>{titulo}</span><strong>{valor}</strong></div>")
        contenido.append("</div><div class='card'>")
        contenido.append(f"<p><b>Mayor carga:</b> {escape(mayor_catedratico)} ({horas.get(mayor_catedratico, 0):.2f} horas)</p><p><b>Aula con mayor ocupación:</b> {escape(mayor_aula)} ({ocupacion.get(mayor_aula, 0)} clases)</p><p><b>Promedio de horas por catedrático:</b> {promedio:.2f}</p></div>")
        contenido.append("<div class='card'><h2>Ocupación de aulas</h2><table><tr><th>Aula</th><th>Clases</th><th>Ocupación estimada</th></tr>")
        for aula in horario.aulas:
            clases = ocupacion.get(aula.codigo, 0)
            porcentaje = min(100, clases / 60 * 100)
            clase_css = "choque" if porcentaje > 80 else ""
            contenido.append(f"<tr class='{clase_css}'><td>{escape(aula.codigo)}</td><td>{clases}</td><td><div class='bar'><span style='width:{porcentaje:.1f}%'></span></div>{porcentaje:.1f}%</td></tr>")
        contenido.append("</table></div>")
        destino = self.salida / "estadistico_general.html"
        destino.write_text(_pagina("Estadístico general del ciclo", "".join(contenido)), encoding="utf-8")
        return destino

    def generar_errores(self, errores: list[ErrorLexico]) -> Path:
        filas = ["<table><tr><th>Número</th><th>Lexema</th><th>Tipo</th><th>Descripción</th><th>Posición</th></tr>"]
        for error in errores:
            filas.append(f"<tr class='choque'><td>{error.numero}</td><td>{escape(error.lexema)}</td><td>{escape(error.tipo)}</td><td>{escape(error.descripcion)}</td><td>{error.linea}:{error.columna}</td></tr>")
        filas.append("</table>" if errores else "</table><div class='card'>No se encontraron errores léxicos.</div>")
        destino = self.salida / "errores_lexicos.html"
        destino.write_text(_pagina("Errores léxicos", "".join(filas)), encoding="utf-8")
        return destino

    def generar_dot(self, horario: Horario) -> Path:
        lineas = ["digraph HorarioScript {", "  rankdir=LR;", "  node [shape=box, style=filled, fillcolor=lightblue];", '  horario [label="HORARIO", fillcolor="#12355b", fontcolor="white"];']
        for grupo, elementos, etiqueta in (("cursos", horario.cursos, "CURSOS"), ("catedraticos", horario.catedraticos, "CATEDRATICOS"), ("aulas", horario.aulas, "AULAS")):
            lineas.append(f'  {grupo} [label="{etiqueta}"]; horario -> {grupo};')
            for indice, elemento in enumerate(elementos):
                nombre = getattr(elemento, "codigo", str(indice)).replace('"', "'")
                nodo = f"{grupo}_{indice}"
                lineas.append(f'  {nodo} [label="{nombre}"]; {grupo} -> {nodo};')
        lineas.append('  clases [label="CLASES"]; horario -> clases;')
        for indice, clase in enumerate(horario.clases):
            nodo = f"clase_{indice}"
            lineas.append(f'  {nodo} [label="{clase.curso}\\n{clase.dia} {clase.inicio}-{clase.fin}"]; clases -> {nodo};')
        lineas.append("}")
        destino = self.salida / "horario.dot"
        destino.write_text("\n".join(lineas), encoding="utf-8")
        return destino

    def generar_todos(self, horario: Horario, errores: list[ErrorLexico]) -> dict[str, Path]:
        return {"horario": self.generar_horario_semanal(horario), "carga": self.generar_carga_catedraticos(horario), "estadistico": self.generar_estadistico(horario), "errores": self.generar_errores(errores), "dot": self.generar_dot(horario)}

