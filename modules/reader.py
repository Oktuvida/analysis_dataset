from typing import Iterator


class SqlReader:
    """
    A SQL file reader.
    """

    def __init__(self, file: str) -> None:
        """
        Arguments:
            file: str
                The path to the location of .sql file 

        Private attributes:
            file
        """

        format = "sql"
        assert file.split(".")[1] == format, ValueError(
            f"Error. The file must be in \".{format}\" format")
        self.__file = file

    def get_queries(self) -> list[str]:
        """
        get all the queries present in the file.

        Returns:
            A list of queries, separated by ";" and taking into account multi-line texts with "$$".
        """

        queries = [""]
        with open(self.__file) as file:
            add_query = True
            for line in file.readlines():
                line = line.strip()
                if line:
                    queries[-1] += " " + line
                    if line.count("$$") == 1:
                        add_query = not add_query
                    if add_query and line[-1] == ";":
                        queries.append("")
        if not queries[-1]:
            queries.pop()
        return queries


class CsvReader:
    """
    A CSV file reader. 
    You can get the columns or rows from it, 
    regardless of whether there are column values with characters equal to the delimiter.
    """

    def __init__(self, file: str, delimiter: str = ',') -> None:
        """
        Arguments:
            file: str
                The path to the location of .csv file

        Public attributes:
            delimiter: str
                The delimiter with which the CSV file will be evaluated.

        Private attributes:
            file
        """

        format = "csv"
        file_splitted = file.split('.')
        assert file_splitted[1] == format, ValueError(
            f"Error. The file must be in \".{format}\" format")
        self.delimiter = delimiter
        self.__file = file
        self.__headers = self.get_headers()

    def __get_columns(
            self, row: str,
            filtered_columns: list[int] | slice = slice(0, None)
        ) -> list[str] | None:
        """
        Get the columns of a row.

        Arguments:
            row: str
        
        Optional arguments:
            filtered_columns: list[int] | slice = slice(0, None)

        Returns:
            A list with the value of each column of the row, or null if the row is empty.
        """

        row = row.strip()
        if len(row) == 0:
            return None

        in_quotes = False
        last_line = ""
        columns = []
        for char in row:
            if char == '"':
                in_quotes = not in_quotes
            elif char != self.delimiter or in_quotes:
                last_line += char
            else:
                columns.append(last_line)
                last_line = ""
        columns.append(last_line)
        match filtered_columns:
            case slice():
                return columns[filtered_columns]
            case list():
                return [columns[i] for i in filtered_columns]
            case _:
                raise ValueError(f"The data type {type(filtered_columns)} of filtered columns isn't valid")

    def get_headers(
        self, filtered_headers: slice | list[int] = slice(0, None)
    ) -> list[str] | None:
        """
        Get the headers from the CSV file

        Optional arguments:
            filtered_headers: slice | list[int]
                The desired headers. By default they are all.

        Returns:
            A list with the name of each header.
        """

        return list(self.get_rows(row_limit = 1, filtered_columns = filtered_headers, with_headers = True))[0]

    def get_rows(
        self, row_limit: int = -1,
        filtered_columns: slice | list[int | str] = slice(0, None),
        with_headers: bool = False
    ) -> Iterator[list[str]]:
        """ 
        Get the rows from the CSV file.

        Optional arguments:
            row_limit: int
                The number of rows. By default they are all.
            filtered_columns: slice | list[int | str]
                Columns for each row. By default they are all.
            with_headers: bool

        Returns:
            A csv row iterator.
        """
        if isinstance(filtered_columns, list):
            for index, column in enumerate(filtered_columns):
                match column:
                    case int():
                        assert 0 <= column < len(self.__headers), ValueError(f"{column} isn't in the columns size range")
                    case str():
                        filtered_columns[index] = self.__headers.index(column)
                    case _:
                        raise ValueError(f"{column} isn't a valid value")

        with open(self.__file) as file:
            if not with_headers:
                file.readline()
            num_row = 0
            while num_row != row_limit:
                line = self.__get_columns(file.readline(), filtered_columns)
                if line is None:
                    break
                yield line
                num_row += 1
