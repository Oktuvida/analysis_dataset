import zipfile
from os import path
from pycountry_convert import (
    country_alpha2_to_continent_code,
    country_alpha3_to_country_alpha2,
)
from modules.executors import SqlExecutor
from modules.objects import SqlTable
from modules.readers import CsvReader
from settings import Connection, Files, TableReference, Variables


def initialize_tables() -> None:
    """
    The initialization of an equivalent of how our tables are in the database.
    """

    Variables.Sql.TABLES = {
        TableReference.DESCRIPCION_DEMOGRAFICA: SqlTable(
            name="DescripcionDemografica",
            columns=[
                "id",
                "id_OficinaRegistro",
                "id_NivelAcademico",
                "id_Especializacion",
                "id_Genero",
                "edad",
                "estatura",
                "cantidad_personas",
            ],
            identifier="id",
            has_incrementable_id=True,
        ),
        TableReference.ESPECIALIZACION: SqlTable(
            name="Especializacion",
            columns=["id", "nombre", "id_AreaConocimiento"],
            identifier="nombre",
            has_incrementable_id=True,
        ),
        TableReference.AREA_CONOCIMIENTO: SqlTable(
            name="AreaConocimiento",
            columns=["id", "nombre"],
            identifier="nombre",
            has_incrementable_id=True,
        ),
        TableReference.NIVEL_ACADEMICO: SqlTable(
            name="NivelAcademico",
            columns=["id", "nombre"],
            identifier="nombre",
            has_incrementable_id=True,
        ),
        TableReference.PAIS: SqlTable(
            name="Pais",
            columns=["id", "id_Continente", "codigo", "nombre"],
            identifier="codigo",
            has_incrementable_id=True,
        ),
        TableReference.CONTINENTE: SqlTable(
            name="Continente",
            columns=["id", "codigo", "nombre"],
            identifier="codigo",
            has_incrementable_id=True,
        ),
        TableReference.OFICINA_REGISTRO: SqlTable(
            name="OficinaRegistro",
            columns=["id", "id_Pais", "nombre"],
            identifier="nombre",
            has_incrementable_id=True,
        ),
        TableReference.GENERO: SqlTable(
            name="Genero",
            columns=["id", "nombre"],
            identifier="nombre",
            has_incrementable_id=True,
        ),
    }


def data_insertion() -> None:
    """
    Insert the CSV rows to the database.

    First we verify that all tables are empty
    and then initialize the CSV reader, the SQL executor and the continents,
    which are not in the CSV file.

    Then we read and select the columns that we will use for each row,
    we obtain the continent using the iso code of the country and we
    perform the insertion in each table sorted by how many relations
    it has (from smallest to largest), saving each query in a queue
    (which is being simulated with a simple string).

    At the end we connect to the database and execute the queue.

    --------------------------------------------

    Insertar las filas del CSV a la base de datos.

    Primero verificamos que todas las tablas estén vacías
    para luego inicializar el lector de CSV, el ejecutor SQL y los continentes,
    los cuales no están en el archivo CSV.

    Luego se leen y se seleccionan las columnas que usaremos por cada fila,
    obtenemos el continente mediante el código iso del país y realizamos
    la inserción en cada tabla ordenadas según cuántas relaciones tenga (de menor a mayor),
    guardando cada consulta en una cola (la cual está siendo simulada con un simple string)

    Al final se conecta a la base de datos y se ejecuta la cola.
    """

    def check_data(reference: TableReference) -> None:
        assert (
            len(Variables.Sql.TABLES[reference].get_values(["limit 1"]) or []) == 0
        ), "The tables in the database aren't empty."

    TableReference.for_each(check_data)

    csv_reader = CsvReader(Files.CSV)
    sql_executor = SqlExecutor(
        database=Connection.DATABASE,
        user=Connection.USER,
        password=Connection.PASSWORD,
        host=Connection.HOST,
        port=Connection.PORT,
    )
    continents = {
        "NA": "North America",
        "SA": "South America",
        "AS": "Asia",
        "OC": "Australia",
        "AF": "Africa",
        "EU": "Europe",
    }
    query = ""
    print("reading and parsing the csv file...")
    for row in csv_reader.get_rows():

        (
            nombre_pais,
            codigo_iso_pais,
            oficina_registro,
            _,
            edad,
            area_conocimiento,
            especializacion,
            nivel_academico,
            _,
            genero,
            _,
            estatura,
            _,
            cantidad_personas,
        ) = row

        if edad == "-1":
            edad = Variables.Sql.NULL_VALUE

        if estatura == "-1":
            estatura = Variables.Sql.NULL_VALUE

        if (
            codigo_iso_pais in ["DDD"]
            or codigo_iso_pais in Variables.Sql.INVALID_VALUES
        ):
            codigo_iso_continente = Variables.Sql.NULL_VALUE
        elif codigo_iso_pais in ["SX"]:
            codigo_iso_continente = "NA"
            codigo_iso_pais = "SXM"
        else:
            codigo_iso_continente = country_alpha2_to_continent_code(
                country_alpha3_to_country_alpha2(codigo_iso_pais)
            )

        query += Variables.Sql.TABLES[TableReference.CONTINENTE].insert_values(
            [
                codigo_iso_continente,
                continents.get(codigo_iso_continente, Variables.Sql.NULL_VALUE),
            ]
        )

        query += Variables.Sql.TABLES[TableReference.PAIS].insert_values(
            [
                Variables.Sql.TABLES[
                    TableReference.CONTINENTE
                ].get_id_by_identifier_value(codigo_iso_continente),
                codigo_iso_pais,
                nombre_pais,
            ]
        )

        query += Variables.Sql.TABLES[TableReference.OFICINA_REGISTRO].insert_values(
            [
                Variables.Sql.TABLES[TableReference.PAIS].get_id_by_identifier_value(
                    codigo_iso_pais
                ),
                oficina_registro,
            ]
        )

        query += Variables.Sql.TABLES[TableReference.NIVEL_ACADEMICO].insert_values(
            [nivel_academico]
        )

        query += Variables.Sql.TABLES[TableReference.AREA_CONOCIMIENTO].insert_values(
            [area_conocimiento]
        )

        query += Variables.Sql.TABLES[TableReference.ESPECIALIZACION].insert_values(
            [
                especializacion,
                Variables.Sql.TABLES[
                    TableReference.AREA_CONOCIMIENTO
                ].get_id_by_identifier_value(area_conocimiento),
            ]
        )

        query += Variables.Sql.TABLES[TableReference.GENERO].insert_values([genero])

        query += Variables.Sql.TABLES[
            TableReference.DESCRIPCION_DEMOGRAFICA
        ].insert_values(
            [
                Variables.Sql.TABLES[
                    TableReference.OFICINA_REGISTRO
                ].get_id_by_identifier_value(oficina_registro),
                Variables.Sql.TABLES[
                    TableReference.NIVEL_ACADEMICO
                ].get_id_by_identifier_value(nivel_academico),
                Variables.Sql.TABLES[
                    TableReference.ESPECIALIZACION
                ].get_id_by_identifier_value(especializacion),
                Variables.Sql.TABLES[TableReference.GENERO].get_id_by_identifier_value(
                    genero
                ),
                edad,
                estatura,
                cantidad_personas,
            ]
        )

    print("It's time to run that huge query!")
    sql_executor.run_query(query)


def prepare_files() -> None:
    if not path.exists(Files.CSV):
        with zipfile.ZipFile(f"{Files.CSV}.zip") as zip_file:
            zip_file.extractall(Files.PATH)
