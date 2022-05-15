from modules.executor import SqlExecutor
from modules.parser import SqlParser
from rich.table import Table
from rich.console import Console
from settings import Connection, Variables


class SqlTable:
    """
    A simple implementation of a SQL table
    """

    def __init__(
        self, name: str, columns: list[str],
        identifier: str | int,
        has_incrementable_id: bool
    ) -> None:
        """
        Arguments:
            name: str
                The table name.
            columns: list[str]
                The table columns.
            identifier: str | int
                The table identifier. 
                Table inserts rely on this for uniqueness, 
                so it is similar to the primary key, but does not necessarily have to be this one.
            has_incrementable_id:
                The id is assumed to be the primary key, and it is inquired whether it 
                is incrementable to take it into account in each insertion.

        Private attributes:
            name: str
                The table name.
            joined_columns: str
                The table columns, joined by commas and quotation marks.
            columns: list[str]
                The table columns.
            records: dict[str, int]
                A dictionary that as key has the identifier and as value the id.
            id: int | None
                The id of the table. 
                If it is specified that it is not incrementable it will not be taken into account in the insertions,
                otherwise, it will start counting from 0 (initializing to -1).
            identifier_index: int
                Instead of storing the name of the identifier, its index is stored in relation to the column.
        """

        self.__name = name
        self.__joined_columns = ','.join([f'"{column}"' for column in columns])
        self.__columns = self.__joined_columns.split(',')

        self.__records: dict[str, int] = dict()
        for invalid_value in Variables.Sql.INVALID_VALUES:
            self.__records[hash(invalid_value)] = Variables.Sql.NULL_VALUE
        self.__records[hash(Variables.Sql.NULL_VALUE)
                       ] = Variables.Sql.NULL_VALUE

        match identifier:
            case int():
                self.__identifier_index = identifier
            case str():
                self.__identifier_index = columns.index(identifier)

        self.__id = None
        if has_incrementable_id:
            self.__id = -1

    def __find_and_hash_identifier(self, values: list[str]) -> int:
        """
        Get the hash value of the identifier within the given values.

        Arguments:
            values: list[str]
                The values of a row.

        Returns:
            An integer, obtained by hashing the value of the identifier.    
        """

        return hash(values[self.__identifier_index])

    def get_id_by_identifier_value(self, identifier_value: str) -> int | str:
        return self.__records[hash(identifier_value)]

    def record_already_exists(self, values: list[str]) -> bool:
        """
        Know if an identifier has already been inserted in the table.

        Arguments:
            values: list[str]
                The values of a row.

        Returns:
            A value obtained by searching the key of the registers for the identifier.
        """

        return self.__find_and_hash_identifier(values) in self.__records

    def insert_values(self, values: list[str]) -> str:
        """
        Simulate the insertion of a row, taking into account the uniqueness of the identifier.

        Arguments:
            values: list[str]
                The values of a row.

        Returns:
            A text string equivalent to a SQL insert. If repeated, an empty string is returned.
        """

        if self.__id is None and not self.record_already_exists(values):
            return SqlParser.get_insert_query(self.__name, self.__joined_columns, values)

        values = [self.__id + 1, *values]
        if not self.record_already_exists(values):
            self.__id += 1
            self.__records[self.__find_and_hash_identifier(values)] = self.__id
            return SqlParser.get_insert_query(self.__name, self.__joined_columns, values)
        return ""

    def __get_values(self, from_statement: str, columns: str, filters: str) -> list[str]:
        sql_executor = SqlExecutor(
            Connection.DATABASE,
            Connection.USER,
            Connection.PASSWORD,
            Connection.HOST,
            Connection.PORT
        )

        return sql_executor.run_query(SqlParser.get_select_query(from_statement, columns, filters))

    def get_values(self, filters: list[str] = []) -> list[str]:
        """
        Get the values of all the columns of the table. 

        Arguments:
            filters: list[str]
                All filters applied to the data after the FROM statement. 
                For example, ["order by 1 2", "limit 10"],
                to sort the data according to the first two columns and limit the results to 10.
        """

        return self.__get_values(f'"{self.__name}"', "*", filters)

    def __join_with_other_tables(self, tables: list['SqlTable']) -> tuple[str, list[str], list[str]]:
        """
        Obtain all the necessary parameters to make a select query with several tables.

        Arguments:
            tables: list[SqlTable]
                The tables with which you want to JOIN. 
                It is important to remember that we only consider the following conditional 
                (which goes in the ON): A.id_B = B.id, where A is the name of the root table 
                and B the name of the tables passed in this argument.

        Returns:
            A tuple with the following values:
            the from statement,
            a list with the name of the columns
            and a list with the name of the columns along with the table name.
        """

        from_statement = f'"{self.__name}"'
        table_columns = self.__columns.copy()
        columns_with_table_name = [
            f""""{self.__name}".{column}""" for column in self.__columns]
        for table in tables:
            if not isinstance(table, SqlTable):
                raise ValueError("Not all items in tables to join are tables")
            from_statement += f"""
                JOIN "{table.__name}"
                ON 
                    ("{table.__name}"."id" = "{self.__name}"."id_{table.__name}")
            """
            table_columns.extend(table.__columns)
            columns_with_table_name.extend(
                f""""{table.__name}".{column}""" for column in table.__columns)
        return (from_statement, table_columns, columns_with_table_name)

    def display(
        self,
        filters: list[str] = ["limit 15"],
        columns: list[str | int] | slice = slice(0, None),
        tables_to_join: list['SqlTable'] = []
    ) -> None:
        """
        Print in console the tuples of the table.

        Optional arguments:
            filters: list[str]
                All filters applied to the data after the FROM statement. 
                For example, ["order by 1 2", "limit 10"],
                to sort the data according to the first two columns and limit the results to 10.
            columns: list[str | int] | slice
                The columns to be displayed.
            tables_to_join: list[SqlTable]
                The tables with which you want to JOIN. 
                It is important to remember that we only consider the following conditional 
                (which goes in the ON): A.id_B = B.id, where A is the name of the root table 
                and B the name of the tables passed in this argument.
        """

        if not isinstance(tables_to_join, list):
            raise ValueError(f"The tables to join aren't a list")

        if not isinstance(filters, list):
            raise ValueError("The filters aren't a list")

        from_statement, table_columns, columns_with_table_name = \
            self.__join_with_other_tables(tables_to_join)

        match columns:
            case slice():
                columns_with_table_name = columns_with_table_name[columns]
            case list():
                for i, column in enumerate(columns):
                    if isinstance(column, str):
                        columns[i] = table_columns.index(f'"{column}"')
                columns_with_table_name = [
                    columns_with_table_name[i] for i in columns]
            case _:
                raise ValueError("The columns aren't a list or a slice")

        output_table = Table(title=self.__name, show_lines=True)
        for column in columns_with_table_name:
            output_table.add_column(
                column.replace('"', '').replace(".", "\n"),
                vertical="middle",
                justify="center"
            )
        for row in self.__get_values(columns=','.join(columns_with_table_name), from_statement=from_statement, filters=filters):
            output_table.add_row(*[str(data) for data in row])

        console = Console()
        console.print(output_table)
