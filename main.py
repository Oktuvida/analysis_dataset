#!/usr/bin/env python

from os import path
from pycountry_convert import country_alpha2_to_continent_code, country_alpha3_to_country_alpha2
from modules.executor import SqlExecutor
from modules.object import SqlTable
from modules.reader import CsvReader
from rich.console import Console
from rich.tree import Tree
from settings import Connection, Files, Variables, TableReference
import zipfile


def initialize_tables() -> None:
    """
    The initialization of an equivalent of how our tables are in the database.  
    """

    global sql_tables
    sql_tables = {
        TableReference.DESCRIPCION_DEMOGRAFICA: SqlTable(
            name="DescripcionDemografica",
            columns=[
                "id", "id_OficinaRegistro", "id_NivelAcademico",
                "id_Especializacion", "edad", "genero",
                "estatura", "cantidad_personas"
            ],
            identifier="id",
            has_incrementable_id=True
        ),
        TableReference.ESPECIALIZACION: SqlTable(
            name="Especializacion",
            columns=[
                "id", "nombre", "id_AreaConocimiento"
            ],
            identifier="nombre",
            has_incrementable_id=True
        ),
        TableReference.AREA_CONOCIMIENTO: SqlTable(
            name="AreaConocimiento",
            columns=[
                "id", "nombre"
            ],
            identifier="nombre",
            has_incrementable_id=True
        ),
        TableReference.NIVEL_ACADEMICO: SqlTable(
            name="NivelAcademico",
            columns=[
                "id", "nombre"
            ],
            identifier="nombre",
            has_incrementable_id=True
        ),
        TableReference.PAIS: SqlTable(
            name="Pais",
            columns=[
                "id", "id_Continente", "codigo", "nombre"
            ],
            identifier="codigo",
            has_incrementable_id=True
        ),
        TableReference.CONTINENTE: SqlTable(
            name="Continente",
            columns=[
                "id", "codigo", "nombre"
            ],
            identifier="codigo",
            has_incrementable_id=True
        ),
        TableReference.OFICINA_REGISTRO: SqlTable(
            name="OficinaRegistro",
            columns=[
                "id", "id_Pais", "nombre"
            ],
            identifier="nombre",
            has_incrementable_id=True
        )
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
        assert len(sql_tables[reference].get_values(
            ["limit 1"])) == 0, "The tables in the database aren't empty."
    TableReference.for_each(check_data)

    csv_reader = CsvReader(Files.CSV)
    sql_executor = SqlExecutor(
        database=Connection.DATABASE,
        user=Connection.USER,
        password=Connection.PASSWORD,
        host=Connection.HOST,
        port=Connection.PORT
    )
    continents = {
        'NA': 'North America',
        'SA': 'South America',
        'AS': 'Asia',
        'OC': 'Australia',
        'AF': 'Africa',
        'EU': 'Europe'
    }
    query = ""
    print("reading and parsing the csv file...")
    for row in csv_reader.get_rows(row_limit=-1):

        nombre_pais, codigo_iso_pais, oficina_registro, \
            _, edad, area_conocimiento, especializacion, \
            nivel_academico, _, genero, _, estatura, _, \
            cantidad_personas = row

        if edad == "-1":
            edad = Variables.Sql.NULL_VALUE

        if estatura == "-1":
            estatura = Variables.Sql.NULL_VALUE

        if codigo_iso_pais in ["DDD"] or codigo_iso_pais in Variables.Sql.INVALID_VALUES:
            codigo_iso_continente = Variables.Sql.NULL_VALUE
        elif codigo_iso_pais in ["SX"]:
            codigo_iso_continente = "NA"
        else:
            codigo_iso_continente = country_alpha2_to_continent_code(
                country_alpha3_to_country_alpha2(codigo_iso_pais)
            )

        query += sql_tables[TableReference.CONTINENTE].insert_values([
            codigo_iso_continente,
            continents.get(codigo_iso_continente, Variables.Sql.NULL_VALUE)
        ])

        query += sql_tables[TableReference.PAIS].insert_values([
            sql_tables[TableReference.CONTINENTE].get_id_by_identifier_value(
                codigo_iso_continente),
            codigo_iso_pais, nombre_pais
        ])

        query += sql_tables[TableReference.OFICINA_REGISTRO].insert_values([
            sql_tables[TableReference.PAIS].get_id_by_identifier_value(
                codigo_iso_pais),
            oficina_registro
        ])

        query += sql_tables[TableReference.NIVEL_ACADEMICO].insert_values([
            nivel_academico
        ])

        query += sql_tables[TableReference.AREA_CONOCIMIENTO].insert_values([
            area_conocimiento
        ])

        query += sql_tables[TableReference.ESPECIALIZACION].insert_values([
            especializacion,
            sql_tables[TableReference.AREA_CONOCIMIENTO].get_id_by_identifier_value(
                area_conocimiento
            )
        ])

        query += sql_tables[TableReference.DESCRIPCION_DEMOGRAFICA].insert_values([
            sql_tables[TableReference.OFICINA_REGISTRO].get_id_by_identifier_value(
                oficina_registro
            ),
            sql_tables[TableReference.NIVEL_ACADEMICO].get_id_by_identifier_value(
                nivel_academico
            ),
            sql_tables[TableReference.ESPECIALIZACION].get_id_by_identifier_value(
                especializacion
            ),
            edad, genero, estatura, cantidad_personas
        ])

    print("It's time to run that huge query!")
    sql_executor.run_query(query)


def get_menu_option() -> str:
    return str(input("""\
    \n1. Insert all the data from the csv to the database.\
    \n2. Print a table\
    \n3. Exit\
    \nPlease, select an option: """))


def get_table_view_option() -> str:
    """
    It prints in console a table and all the possible combinations 
    that we have implemented in the form of a tree, to then request some option.
    """

    global table_index, table_view_limit
    possible_combinations = Tree(" Possible table views ")

    table_index = 0

    def set_title(text: str) -> str:
        global table_index
        table_index += 1
        return f"{table_index}. {text}"

    descripcion_demografica = Tree(set_title("DescripcionDemografica"))

    especializacion = descripcion_demografica.add(set_title("Especializacion"))
    especializacion.add(set_title("NivelAcademico"))\
        .add(set_title("OficinaRegistro"))
    especializacion.add(set_title("OficinaRegistro"))

    descripcion_demografica.add(set_title("NivelAcademico"))\
        .add(set_title("OficinaRegistro"))

    descripcion_demografica.add(set_title("OficinaRegistro"))

    especializacion = Tree(set_title("Especializacion"))
    especializacion.add(set_title("AreaConocimiento"))

    oficina_registro = Tree(set_title("OficinaRegistro"))
    oficina_registro.add(set_title("Pais"))

    pais = Tree(set_title("Pais"))
    pais.add(set_title("Continente"))

    possible_combinations.add(descripcion_demografica)
    possible_combinations.add(especializacion)
    possible_combinations.add(oficina_registro)
    possible_combinations.add(pais)
    possible_combinations.add(set_title("Continente"))
    possible_combinations.add(set_title("AreaConocimiento"))
    possible_combinations.add(set_title("NivelAcademico"))

    console = Console()
    console.print(possible_combinations)
    print(set_title("Change actual limit view"))
    print(set_title("Back"))
    return str(input("Please, select an option: "))


def table_view_menu() -> None:
    global table_index, table_view_limit

    def display_table(reference: TableReference, tables_to_join: list[SqlTable] = []) -> None:
        global table_view_limit
        if table_view_limit < 0:
            filters = ["order by 1"]
        else:
            filters = ["order by 1", f"limit {table_view_limit}"]

        sql_tables[reference].display(
            tables_to_join=tables_to_join,
            filters=filters
        )

    while (option := get_table_view_option()) != str(table_index):
        match option:
            case "1":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA)
            case "2":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.ESPECIALIZACION],
                ])
            case "3":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.ESPECIALIZACION],
                    sql_tables[TableReference.NIVEL_ACADEMICO],
                ])
            case "4":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.ESPECIALIZACION],
                    sql_tables[TableReference.NIVEL_ACADEMICO],
                    sql_tables[TableReference.OFICINA_REGISTRO],
                ])
            case "5":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.ESPECIALIZACION],
                    sql_tables[TableReference.OFICINA_REGISTRO],
                ])
            case "6":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.NIVEL_ACADEMICO],
                ])
            case "7":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.NIVEL_ACADEMICO],
                    sql_tables[TableReference.OFICINA_REGISTRO],
                ])
            case "8":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA, [
                    sql_tables[TableReference.OFICINA_REGISTRO],
                ])
            case "9":
                display_table(TableReference.ESPECIALIZACION)
            case "10":
                display_table(TableReference.ESPECIALIZACION, [
                    sql_tables[TableReference.AREA_CONOCIMIENTO],
                ])
            case "11":
                display_table(TableReference.OFICINA_REGISTRO)
            case "12":
                display_table(TableReference.OFICINA_REGISTRO, [
                    sql_tables[TableReference.PAIS],
                ])
            case "13":
                display_table(TableReference.PAIS)
            case "14":
                display_table(TableReference.PAIS, [
                    sql_tables[TableReference.CONTINENTE]
                ])
            case "15":
                display_table(TableReference.CONTINENTE)
            case "16":
                display_table(TableReference.AREA_CONOCIMIENTO)
            case "17":
                display_table(TableReference.NIVEL_ACADEMICO)
            case "18":
                table_view_limit = int(
                    input("Enter the limit of data to display that you want (negative values will display all): "))
            case _:
                continue
        print(
            f"A maximum of {table_view_limit} results are currently being printed.")
        input("Press Enter to continue...")


def menu() -> None:
    global table_view_limit
    table_view_limit = 15
    while (menu_option := get_menu_option()) != "3":
        match menu_option:
            case "1":
                data_insertion()
            case "2":
                table_view_menu()
            case _:
                print("Invalid option. Try again")
        print()


def main() -> None:
    if not path.exists(Files.CSV):
        with zipfile.ZipFile(f"{Files.CSV}.zip") as zip_file:
            zip_file.extractall(Files.PATH)
    initialize_tables()
    menu()


if __name__ == "__main__":
    main()
