import dash_bootstrap_components as dbc
from dash import html


class Sidebar:
    def __init__(self, title: str, description: str = "", id: str = "") -> None:
        self.__header = html.Div([html.H2(title), html.Hr(), html.P(description)])
        self.__childs = []
        self.__id = "sidebar"

    def add_link(self, text: str, href: str, id="", className: str = "") -> None:
        if len(id) > 0:
            self.__childs.append(
                dbc.NavLink(text, href=href, active="exact", className=className, id=id)
            )
        else:
            self.__childs.append(
                dbc.NavLink(text, href=href, active="exact", className=className)
            )

    def get_container(self) -> "html.Div":
        return html.Div(
            [
                self.__header,
                dbc.Nav(self.__childs, vertical=True, pills=True),
            ],
            id=self.__id,
        )


class Table:
    def __init__(
        self, headers: list[str] = [], rows: list[list[str]] | list[tuple] = []
    ) -> None:
        self.__header: html.Thead | None = None
        self.__body: list[html.Tr] = []
        self.__header_size: int = 0
        self.set_header(headers)
        for row in rows:
            self.add_row(row)

    def set_header(self, names: list[str]) -> None:
        self.__header = html.Thead(html.Tr([html.Th(name) for name in names]))
        self.__header_size = len(names)

    def add_row(self, values: list[str] | tuple) -> None:
        assert self.__header_size == len(values), ValueError(
            "Number of columns in the row does not match the headers"
        )
        self.__body.append(html.Tr([html.Td(value) for value in values]))

    def get_container(self) -> "dbc.Table":
        return dbc.Table([self.__header, html.Tbody(self.__body)])
