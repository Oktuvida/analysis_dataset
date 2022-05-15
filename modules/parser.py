from settings import Variables


class SqlParser:
    @staticmethod
    def get_insert_query(table_name: str, columns: list[str] | str, values: list[str | int]) -> str:
        """
        Get an insert query.

        Arguments:
            table_name: str
            columns: list[str]
            values: list[str | int]

        Returns:
            A sql insert query.
        """

        sql_values = ""
        for value in values:
            if isinstance(value, int) or (value[0] == "(" and value[-1] == ")") or value == Variables.Sql.NULL_VALUE:
                sql_values += str(value) + ","
            else:
                sql_values += "'" + value + "',"
        sql_values = sql_values[:-1:]
        match columns:
            case list():
                assert len(columns) == len(
                    values), "columns and values do not have the same size."
                return f"""INSERT INTO "{table_name}"({','.join(f'"{header}"' for header in columns)}) VALUES ({sql_values});"""
            case str():
                return f"""INSERT INTO "{table_name}"({columns}) VALUES ({sql_values});"""
    
    @staticmethod
    def get_select_query(from_statement: str, columns: str = "*", filters: list[str] = []) -> None:
        """
        Get a select query

        Arguments:
            from_statement: str
                The statement that follows the from statement, 
                which includes the tables and their joins.
        
        Optional arguments:
            columns: str
                The selected columns.
            filters: list[str]
                All filters applied to the data after the FROM statement. 
                For example, ["order by 1 2", "limit 10"],
                to sort the data according to the first two columns and limit the results to 10.
        """

        return f"""
        SELECT
            {columns}
        FROM
            {from_statement}
        {' '.join(filters)}
        """
