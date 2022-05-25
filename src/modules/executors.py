from typing import Any, Callable
import psycopg2
import psycopg2.extras


class SqlExecutor:
    """
    A sql query executor.
    """

    def __init__(
        self,
        database: str,
        user: str,
        password: str | None,
        host: str = "127.0.0.1",
        port: str = "5432",
    ) -> None:
        """
        Arguments:
            database: str
                The database name.
            user: str
                The user to log in with.
            password: str
                The user's password.
            host: str
                The IP Address. By default 127.0.0.1.
            port: str
                The port. By default 5432.

        Private attributes:
            database, user, password.
        """

        self.__database = database
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port

    def __connect(self) -> "psycopg2.connection":
        """
        Connect to the database.

        Returns:
            A psycopg2.connection.
        """

        return psycopg2.connect(
            database=self.__database,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port,
        )

    def run_query(
        self,
        query: str,
        params: tuple | None = None,
        handle_conn: Callable | None = None,
    ) -> list[tuple] | None:
        """
        Execute a query

        Arguments:
            query: str
                A sql query.
            params: tuple
            handle_conn: (psycopg2.connection) -> Any

        Returns:
            The query response.
        """

        res = None
        conn: psycopg2.connection
        with self.__connect() as conn:
            if handle_conn is not None:
                res = handle_conn(query, conn)
            else:
                with conn.cursor() as cursor:
                    if params is not None:
                        res = psycopg2.extras.execute_values(
                            cursor,
                            query,
                            params,
                            template=None,
                            page_size=100,
                            fetch=True,
                        )
                    else:
                        cursor.execute(query)
                        if cursor.pgresult_ptr is not None:
                            res = cursor.fetchall()
        return res
