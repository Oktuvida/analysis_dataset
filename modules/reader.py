#Lee las sentencias SQL o CSV.

from typing import Iterator, Union


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

    def __get_columns(self, row: str) -> Union[list[str], None]:
        """
        Get the columns of a row.

        Arguments:
            row: str

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
        return columns

    def get_headers(
        self, filtered_headers: Union[slice, list[int]] = slice(0, None)
    ) -> list[str]:
        """
        Get the headers from the CSV file

        Optional arguments:
            filtered_headers: slice | list[int]
                The desired headers. By default they are all.
                It can be a slice, e.g. slice(0, 3); 
                it can be a list of integers, e.g [1, 3].

        Returns:
            A list with the name of each header.
        """

        headers = []
        with open(self.__file) as file:
            line = self.__get_columns(file.readline())
            if line is not None:
                match filtered_headers:
                    case slice():
                        headers = line[filtered_headers]
                    case list():
                        headers = [line[i] for i in filtered_headers]
        return headers

    def get_rows(
        self, row_limit: int = -1,
        filtered_columns: Union[slice, list[int], list[str]] = slice(0, None),
    ) -> Iterator[list[str]]:
        """ 
        Get the rows from the CSV file.

        Optional arguments:
            row_limit: int
                The number of rows. By default they are all.
            filtered_columns: slice | list[int] | list[str]
                Columns for each row. By default they are all.
                It can be a slice, e.g. slice(1, 5); 
                a list with the index corresponding to the column, e.g. [1, 5, 9];
                a list with the exact name corresponding to the column, e.g. ["Hello", "World!"].

        Returns:
            A csv row iterator.
        """

        with open(self.__file) as file:
            file.readline()
            num_row = 0
            while num_row != row_limit:
                line = self.__get_columns(file.readline())
                if line is None:
                    break
                match filtered_columns:
                    case slice():
                        yield line[filtered_columns]
                    case list():
                        yield [line[i] for i in filtered_columns]
                    case _:
                        raise ValueError(
                            "the filtered columns must be a list or a slice.")
                num_row += 1
