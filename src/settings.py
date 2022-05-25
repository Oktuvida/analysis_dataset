import os
from enum import Enum
from typing import Any, Callable
from dotenv import load_dotenv


if not ".env" in os.listdir(actual_dir := os.getcwd()):
    actual_dir = actual_dir + "/.."

load_dotenv(os.path.join(actual_dir, ".env"))


class Connection:
    DATABASE = str(os.getenv("pg_database"))
    USER = str(os.getenv("pg_user"))
    PASSWORD = str(os.getenv("pg_password"))
    HOST = str(os.getenv("pg_host"))
    PORT = str(os.getenv("pg_port"))


class Server:
    PORT = int(os.getenv("dash_port") or 8050)
    HOST = str(os.getenv("dash_host"))


class Files:
    PATH = actual_dir + "/assets"
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
    GENERO = 8

    @classmethod
    def for_each(cls, function: Callable[["TableReference"], Any]) -> None:
        for const in cls:
            function(const)


class Variables:
    class Sql:
        NULL_VALUE = "null"
        INVALID_VALUES = (
            "NO INDICA",
            "(NO REGISTRA)",
        )
        TABLES = {}
