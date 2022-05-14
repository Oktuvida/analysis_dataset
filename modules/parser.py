#Convierte cadenas de texto a SQL.

from typing import Union

from settings import Variables


class SqlParser:
    @staticmethod
    def get_insert_query(table_name: str, columns: list[str], values: list[Union[str, int]]) -> str:
        """
        Get an insert query

        Arguments:
            table_name: str
            columns: list[str]
            values: list[str | int]

        Returns:
            A sql insert query
        """

        assert len(columns) == len(
            values), "columns and values do not have the same size."
        sql_values = ""
        for value in values:
            if isinstance(value, int) or (value[0] == "(" and value[-1] == ")") or value == Variables.Sql.NULL_VALUE:
                sql_values += str(value) + ","
            else:
                sql_values += "'" + value + "',"
        sql_values = sql_values[:-1:]
        return f"""INSERT INTO "{table_name}"({','.join(f'"{header}"' for header in columns)}) VALUES ({sql_values});"""
