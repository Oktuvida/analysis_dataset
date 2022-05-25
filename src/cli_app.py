#!/usr/bin/env python

from modules.objects import SqlTable
from rich.console import Console
from rich.tree import Tree
from modules.utils import data_insertion, initialize_tables, prepare_files
from settings import TableReference, Variables


def get_menu_option() -> str:
    return str(
        input(
            """\
    \n1. Insert all the data from the csv to the database.\
    \n2. Print a table\
    \n3. Exit\
    \nPlease, select an option: """
        )
    )


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
    especializacion.add(set_title("NivelAcademico")).add(set_title("OficinaRegistro"))
    especializacion.add(set_title("OficinaRegistro"))

    descripcion_demografica.add(set_title("NivelAcademico")).add(
        set_title("OficinaRegistro")
    )

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

    def display_table(
        reference: TableReference, tables_to_join: list[SqlTable] = []
    ) -> None:
        global table_view_limit
        if table_view_limit < 0:
            filters = ["order by 1"]
        else:
            filters = ["order by 1", f"limit {table_view_limit}"]

        Variables.Sql.TABLES[reference].display(
            tables_to_join=tables_to_join, filters=filters
        )

    while (option := get_table_view_option()) != str(table_index):
        match option:
            case "1":
                display_table(TableReference.DESCRIPCION_DEMOGRAFICA)
            case "2":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.ESPECIALIZACION],
                    ],
                )
            case "3":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.ESPECIALIZACION],
                        Variables.Sql.TABLES[TableReference.NIVEL_ACADEMICO],
                    ],
                )
            case "4":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.ESPECIALIZACION],
                        Variables.Sql.TABLES[TableReference.NIVEL_ACADEMICO],
                        Variables.Sql.TABLES[TableReference.OFICINA_REGISTRO],
                    ],
                )
            case "5":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.ESPECIALIZACION],
                        Variables.Sql.TABLES[TableReference.OFICINA_REGISTRO],
                    ],
                )
            case "6":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.NIVEL_ACADEMICO],
                    ],
                )
            case "7":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.NIVEL_ACADEMICO],
                        Variables.Sql.TABLES[TableReference.OFICINA_REGISTRO],
                    ],
                )
            case "8":
                display_table(
                    TableReference.DESCRIPCION_DEMOGRAFICA,
                    [
                        Variables.Sql.TABLES[TableReference.OFICINA_REGISTRO],
                    ],
                )
            case "9":
                display_table(TableReference.ESPECIALIZACION)
            case "10":
                display_table(
                    TableReference.ESPECIALIZACION,
                    [
                        Variables.Sql.TABLES[TableReference.AREA_CONOCIMIENTO],
                    ],
                )
            case "11":
                display_table(TableReference.OFICINA_REGISTRO)
            case "12":
                display_table(
                    TableReference.OFICINA_REGISTRO,
                    [
                        Variables.Sql.TABLES[TableReference.PAIS],
                    ],
                )
            case "13":
                display_table(TableReference.PAIS)
            case "14":
                display_table(
                    TableReference.PAIS,
                    [Variables.Sql.TABLES[TableReference.CONTINENTE]],
                )
            case "15":
                display_table(TableReference.CONTINENTE)
            case "16":
                display_table(TableReference.AREA_CONOCIMIENTO)
            case "17":
                display_table(TableReference.NIVEL_ACADEMICO)
            case "18":
                table_view_limit = int(
                    input(
                        "Enter the limit of data to display that you want (negative values will display all): "
                    )
                )
            case _:
                continue
        print(f"A maximum of {table_view_limit} results are currently being printed.")
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
    prepare_files()
    initialize_tables()
    menu()


if __name__ == "__main__":
    main()
