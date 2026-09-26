from __future__ import annotations

import subprocess
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .service import ResultadoAnalisis, analizar_fuente


class HorarioScriptApp:
    def __init__(self, root: tk.Tk, archivo_inicial: str | None = None) -> None:
        self.root = root
        self.root.title("HorarioScript - Analizador léxico")
        self.root.geometry("1120x720")
        self.archivo: Path | None = None
        self.resultado: ResultadoAnalisis | None = None
        self._construir_interfaz()
        if archivo_inicial:
            self._cargar_ruta(Path(archivo_inicial))

    def _construir_interfaz(self) -> None:
        barra = ttk.Frame(self.root, padding=8)
        barra.pack(fill="x")
        ttk.Button(barra, text="Cargar .hor", command=self.cargar_archivo).pack(side="left", padx=4)
        ttk.Button(barra, text="Analizar", command=self.analizar).pack(side="left", padx=4)
        self.estado = tk.StringVar(value="Seleccione un archivo .hor")
        ttk.Label(barra, textvariable=self.estado).pack(side="left", padx=12)

        cuerpo = ttk.PanedWindow(self.root, orient="horizontal")
        cuerpo.pack(fill="both", expand=True, padx=8, pady=8)
        izquierdo = ttk.Frame(cuerpo, padding=4)
        derecho = ttk.Frame(cuerpo, padding=4)
        cuerpo.add(izquierdo, weight=1)
        cuerpo.add(derecho, weight=2)

        ttk.Label(izquierdo, text="Archivo fuente").pack(anchor="w")
        self.editor = tk.Text(izquierdo, wrap="none", undo=True)
        self.editor.pack(fill="both", expand=True)

        self.pestanas = ttk.Notebook(derecho)
        self.pestanas.pack(fill="both", expand=True)
        self.tab_tokens = ttk.Frame(self.pestanas)
        self.tab_errores = ttk.Frame(self.pestanas)
        self.tab_reportes = ttk.Frame(self.pestanas)
        self.pestanas.add(self.tab_tokens, text="Tokens")
        self.pestanas.add(self.tab_errores, text="Errores léxicos")
        self.pestanas.add(self.tab_reportes, text="Reportes")
        self.tokens_view = self._tabla(self.tab_tokens, ("numero", "lexema", "tipo", "linea", "columna"))
        self.errores_view = self._tabla(self.tab_errores, ("numero", "lexema", "tipo", "descripcion", "posicion"))
        self.reportes_frame = ttk.Frame(self.tab_reportes, padding=12)
        self.reportes_frame.pack(anchor="nw", fill="x")

    @staticmethod
    def _tabla(contenedor, columnas):
        tabla = ttk.Treeview(contenedor, columns=columnas, show="headings")
        for columna in columnas:
            tabla.heading(columna, text=columna.capitalize())
            tabla.column(columna, width=150, anchor="w")
        tabla.pack(fill="both", expand=True)
        return tabla

    def _cargar_ruta(self, ruta: Path) -> None:
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except OSError as error:
            messagebox.showerror("No se pudo abrir", str(error))
            return
        self.archivo = ruta
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", contenido)
        self.estado.set(f"Cargado: {ruta.name}")

    def cargar_archivo(self) -> None:
        ruta = filedialog.askopenfilename(filetypes=(("HorarioScript", "*.hor"), ("Todos", "*.*")))
        if ruta:
            self._cargar_ruta(Path(ruta))

    def analizar(self) -> None:
        fuente = self.editor.get("1.0", "end-1c")
        salida = (self.archivo.parent / "reportes") if self.archivo else Path("reportes")
        self.resultado = analizar_fuente(fuente, salida)
        for item in self.tokens_view.get_children():
            self.tokens_view.delete(item)
        for token in self.resultado.tokens:
            if token.tipo.value != "EOF":
                self.tokens_view.insert("", "end", values=(token.numero, token.lexema, token.tipo.value, token.linea, token.columna))
        for item in self.errores_view.get_children():
            self.errores_view.delete(item)
        for error in self.resultado.errores_lexicos:
            self.errores_view.insert("", "end", values=(error.numero, error.lexema, error.tipo, error.descripcion, f"{error.linea}:{error.columna}"))
        self._actualizar_reportes()
        self.estado.set(f"Análisis terminado: {len(self.resultado.errores_lexicos)} error(es), {len(self.resultado.horario.choques)} choque(s)")

    def _actualizar_reportes(self) -> None:
        for widget in self.reportes_frame.winfo_children():
            widget.destroy()
        if not self.resultado:
            return
        for nombre, ruta in self.resultado.reportes.items():
            if ruta.suffix == ".html":
                ttk.Button(self.reportes_frame, text=f"Abrir {nombre}", command=lambda path=ruta: webbrowser.open(path.resolve().as_uri())).pack(anchor="w", pady=3)
            else:
                ttk.Button(self.reportes_frame, text=f"Ver {nombre}", command=lambda path=ruta: self._abrir_texto(path)).pack(anchor="w", pady=3)

    @staticmethod
    def _abrir_texto(ruta: Path) -> None:
        if sys.platform.startswith("win"):
            subprocess.Popen(["notepad.exe", str(ruta)])
        else:
            webbrowser.open(ruta.resolve().as_uri())


def iniciar_gui(archivo: str | None = None) -> None:
    root = tk.Tk()
    HorarioScriptApp(root, archivo)
    root.mainloop()

