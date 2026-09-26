from __future__ import annotations

from dataclasses import dataclass, field


def quitar_comillas(valor: str) -> str:
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        return valor[1:-1]
    return valor


def minutos(hora: str) -> int:
    if len(hora) != 5 or hora[2] != ":":
        return 0
    return int(hora[:2]) * 60 + int(hora[3:])


@dataclass
class Curso:
    nombre: str
    codigo: str
    creditos: int


@dataclass
class Catedratico:
    nombre: str
    codigo: str
    categoria: str


@dataclass
class Aula:
    codigo: str
    capacidad: int
    edificio: str


@dataclass
class Clase:
    curso: str
    catedratico: str
    aula: str
    dia: str
    inicio: str
    fin: str
    seccion: str

    @property
    def inicio_minutos(self) -> int:
        return minutos(self.inicio)

    @property
    def fin_minutos(self) -> int:
        return minutos(self.fin)

    @property
    def duracion_horas(self) -> float:
        return max(0, self.fin_minutos - self.inicio_minutos) / 60


@dataclass(frozen=True)
class Choque:
    primera: Clase
    segunda: Clase
    recurso: str


@dataclass
class Horario:
    cursos: list[Curso] = field(default_factory=list)
    catedraticos: list[Catedratico] = field(default_factory=list)
    aulas: list[Aula] = field(default_factory=list)
    clases: list[Clase] = field(default_factory=list)
    choques: list[Choque] = field(default_factory=list)

    def detectar_choques(self) -> list[Choque]:
        encontrados: list[Choque] = []
        for indice, primera in enumerate(self.clases):
            for segunda in self.clases[indice + 1 :]:
                mismo_dia = primera.dia == segunda.dia
                traslape = primera.inicio_minutos < segunda.fin_minutos and segunda.inicio_minutos < primera.fin_minutos
                if not (mismo_dia and traslape):
                    continue
                if primera.catedratico == segunda.catedratico:
                    encontrados.append(Choque(primera, segunda, "CATEDRATICO"))
                if primera.aula == segunda.aula:
                    encontrados.append(Choque(primera, segunda, "AULA"))
        self.choques = encontrados
        return encontrados

