#!/usr/bin/env python

from argparse import ArgumentError
from os import path
from pycountry_convert import country_alpha2_to_continent_code, country_alpha3_to_country_alpha2
from resources.executor import SqlExecutor
from resources.reader import CsvReader
from resources.parser import SqlParser
from settings import Connection, Files, Variables
import zipfile

def data_viewer(
    table_name: str, 
    filters: list[str] = ["limit 15"], 
    columns: list[str | int] | slice = slice(0, None),
    display_column_names: bool = True
) -> None:
    """
    Print in console the tuples of a table

    Arguments:
        table_name: str
            The name of the target table
    
    Optional arguments:
        filters: list[str]
            The filters applied to the query, e.g. ["group by 1 2", "limit 5"]. Its default value is ["limit 15"].
        columns: list[str | int] | slice
            The columns to be selected, e.g. ["hi-mom", 2, 4] or slice(0, 5)
    """

    if not isinstance(filters, list):
        raise ValueError("The filters aren't a list")

    sql_executor = SqlExecutor(
        Connection.DATABASE, Connection.USER, Connection.PASSWORD)
    
    table_columns = sql_executor.run_query(f"""
    SELECT 
        Column_name
    FROM 
        INFORMATION_SCHEMA.COLUMNS
    WHERE 
        TABLE_NAME = '{table_name}'
    """)
    table_columns = [f'"{column[0]}"' for column in table_columns]


    match columns:
        case slice():
            columns_to_display = table_columns[columns]
        case list():
            for i, column in enumerate(columns):
                if isinstance(column, str):
                    columns[i] = table_columns.index(f'"{column}"')
            columns_to_display = [table_columns[i] for i in columns]
        case _:
            raise ValueError("The columns aren't a list or a slice")

    
    if display_column_names:
        print('\t'.join(columns_to_display))
    for row in sql_executor.run_query(f"""SELECT {','.join(columns_to_display)} FROM "{table_name}" {' '.join(filters)}; """):
        print('\t\t'.join([str(i) for i in row]))

def data_insertion() -> None:
    """
    Insert all rows with the columns of interest from the CSV into the database.

    First we initialize the csv reader; the sql query executor; the data we consider invalid; 
    both the columns, the initial value of their id and the record of the primary keys already 
    entered for each table; and a single query that will serve as a queue for all the necessary 
    inserts, separated by semicolons.

    The only thing left is to iterate the rows of the CSV, 
    being the order of execution of the tables according to how 
    many relations it has (from smallest to largest). As soon as 
    it finds that a tuple has not yet been added to the table, 
    i.e. is not yet in the table recorder, it will be added to the query queue.

    -------------------------------------------------------------------

    Insertar todas las filas con las columnas de interés del CSV en la base de datos.

    Primero se inicializa el lector de csv; el ejecutor de consultas sql; los datos que concideramos inválidos;
    tanto las columnas, el valor inicial de su id como el registro de las llaves primarias ya 
    ingresadas de cada tabla; y una única consulta que servirá como cola a todos los inserts necesarios,
    separados por punto y coma.

    Lo único que resta es iterar las filas del CSV,
    siendo el orden de ejecución de las tablas según cuantas
    relaciones tenga esta (de menor a mayor). En el momento
    que encuentre que alguna tupla aún no ha sido agregada a la tabla,
    es decir, que aún no este en registrador de la tabla, será agregada a la cola de la query.
    """

    csv_reader = CsvReader(Files.CSV)
    sql_executor = SqlExecutor(
        database = Connection.DATABASE, 
        user = Connection.USER, 
        password = Connection.PASSWORD,
        host = Connection.HOST,
        port = Connection.PORT
    )

    query = ""
    invalid_values = {"NO INDICA", "(NO REGISTRA)"}

    DescripcionDemografica_columns = [
        "id", "id_OficinaRegistro", "id_NivelAcademico",
        "id_Especializacion", "edad", "genero", 
        "estatura", "cantidad_personas"
    ]
    Especializacion_columns = ["id", "nombre", "id_AreaConocimiento"]
    AreaConocimiento_columns = ["id", "nombre"]
    NivelAcademico_columns = ["id", "nombre"]
    Pais_columns = ["id", "id_Continente", "codigo", "nombre"]
    Continente_columns = ["id", "codigo", "nombre"]
    OficinaRegistro_columns = ["id", "id_Pais", "nombre", "ubicacion"]

    Pais_recorder = dict()
    OficinaRegistro_recorder = dict()
    NivelAcademico_recorder = dict()
    AreaConocimiento_recorder = dict()
    Especializacion_recorder = dict()
    Continente_recorder = dict()

    Pais_id_counter = 0
    OficinaRegistro_id_counter = 0
    NivelAcademico_id_counter = 0
    AreaConocimiento_id_counter = 0
    Especializacion_id_counter = 0
    Continente_id_counter = 0
    DescripcionDemografica_id_counter = 0

    continents = {
    'NA': 'North America',
    'SA': 'South America', 
    'AS': 'Asia',
    'OC': 'Australia',
    'AF': 'Africa',
    'EU': 'Europe'
    }


    print("reading and parsing the csv file...")
    for row in csv_reader.get_rows(row_limit=-1):
        nombre_pais = row[0]
        codigo_iso_pais = row[1]

        if codigo_iso_pais in ["DDD"] or codigo_iso_pais in invalid_values:
            codigo_iso_continente = Variables.Sql.NULL_VALUE
        elif codigo_iso_pais in ["SX"]:
            codigo_iso_continente = "NA"
        else:
            codigo_iso_continente = country_alpha2_to_continent_code(
                country_alpha3_to_country_alpha2(codigo_iso_pais))

        oficina_registro = row[2]
        edad = int(row[4]) if row[4] != "-1" else Variables.Sql.NULL_VALUE
        area_conocimiento = row[5]
        especializacion = row[6]
        nivel_academico = row[7]
        genero = row[9]
        estatura = int(row[11]) if row[11] != "-1" else Variables.Sql.NULL_VALUE
        localizacion = row[12]
        cantidad_personas = int(row[13])

        if codigo_iso_continente not in Continente_recorder:
            if codigo_iso_continente == Variables.Sql.NULL_VALUE:
                Continente_recorder[codigo_iso_continente] = Variables.Sql.NULL_VALUE
            else:
                Continente_recorder[codigo_iso_continente] = Continente_id_counter
                query += SqlParser.get_insert_query(
                    "Continente",
                    Continente_columns,
                    [Continente_id_counter, codigo_iso_continente, continents[codigo_iso_continente]]
                )
                Continente_id_counter += 1

        if codigo_iso_pais not in Pais_recorder:
            if codigo_iso_pais in invalid_values:
                Pais_recorder[codigo_iso_pais] = Variables.Sql.NULL_VALUE
            else:
                Pais_recorder[codigo_iso_pais] = Pais_id_counter
                query += SqlParser.get_insert_query(
                    "Pais",
                    Pais_columns,
                    [Pais_id_counter, Continente_recorder[codigo_iso_continente], codigo_iso_pais, nombre_pais]
                )
                Pais_id_counter += 1

        if oficina_registro not in OficinaRegistro_recorder:
            if oficina_registro in invalid_values:
                OficinaRegistro_recorder[oficina_registro] = Variables.Sql.NULL_VALUE
            else:
                OficinaRegistro_recorder[oficina_registro] = OficinaRegistro_id_counter
                query += SqlParser.get_insert_query(
                    "OficinaRegistro",
                    OficinaRegistro_columns,
                    [OficinaRegistro_id_counter, Pais_recorder[codigo_iso_pais],
                        oficina_registro, localizacion]
                )
                OficinaRegistro_id_counter += 1

        if nivel_academico not in NivelAcademico_recorder:
            if nivel_academico in invalid_values:
                NivelAcademico_recorder[nivel_academico] = Variables.Sql.NULL_VALUE
            else:
                NivelAcademico_recorder[nivel_academico] = NivelAcademico_id_counter
                query += SqlParser.get_insert_query(
                    "NivelAcademico",
                    NivelAcademico_columns,
                    [NivelAcademico_id_counter, nivel_academico]
                )
                NivelAcademico_id_counter += 1

        if area_conocimiento not in AreaConocimiento_recorder:
            if area_conocimiento in invalid_values:
                AreaConocimiento_recorder[area_conocimiento] = Variables.Sql.NULL_VALUE
            else:
                AreaConocimiento_recorder[area_conocimiento] = AreaConocimiento_id_counter
                query += SqlParser.get_insert_query(
                    "AreaConocimiento",
                    AreaConocimiento_columns,
                    [AreaConocimiento_id_counter, area_conocimiento]
                )
                AreaConocimiento_id_counter += 1

        if especializacion not in Especializacion_recorder:
            if especializacion in invalid_values:
                Especializacion_recorder[especializacion] = Variables.Sql.NULL_VALUE
            else:
                Especializacion_recorder[especializacion] = Especializacion_id_counter
                query += SqlParser.get_insert_query(
                    "Especializacion",
                    Especializacion_columns,
                    [Especializacion_id_counter, especializacion,
                        AreaConocimiento_recorder[area_conocimiento]]
                )
                Especializacion_id_counter += 1

        query += SqlParser.get_insert_query(
            "DescripcionDemografica",
            DescripcionDemografica_columns,
            [
                DescripcionDemografica_id_counter,
                OficinaRegistro_recorder[oficina_registro],
                NivelAcademico_recorder[nivel_academico],
                Especializacion_recorder[especializacion],
                edad,
                genero,
                estatura,
                cantidad_personas
            ]
        )
        DescripcionDemografica_id_counter += 1
    print("It's time to run that huge query!")
    sql_executor.run_query(query)


def main() -> None:
    if not path.exists(Files.CSV):
        with zipfile.ZipFile(f"{Files.CSV}.zip") as zip_file:
            zip_file.extractall(Files.PATH)

    data_viewer("Continente")


if __name__ == "__main__":
    main()
