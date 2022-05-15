from enum import Enum
from typing import Any, Callable


class Connection:
    DATABASE = "colombianos_registrados_exterior"
    USER = "postgres"
    PASSWORD = None
    HOST = "127.0.0.1"
    PORT = "5432"


class Files:
    PATH = "data"
    CSV = PATH + "/colombianos_registrados_exterior.csv"
    SQL_DATABASE = PATH + "/colombianos_registrados_exterior.sql"


class TableReference(Enum):
    DESCRIPCION_DEMOGRAFICA = 1
    ESPECIALIZACION = 2
    AREA_CONOCIMIENTO = 3
    NIVEL_ACADEMICO = 4
    PAIS = 5
    CONTINENTE = 6
    OFICINA_REGISTRO = 7

    @classmethod
    def for_each(cls, function: Callable[['TableReference'], Any]) -> None:
        for const in cls:
            function(const)


class Variables:
    class Sql:
        NULL_VALUE = "null"
        INVALID_VALUES = "NO INDICA", "(NO REGISTRA)",
