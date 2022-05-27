import plotly.express as px
import plotly.graph_objects
import pandas as pd
import dash_bootstrap_components as dbc
from typing import Any
from dash import html, dcc
from modules.objects import HtmlTable
from settings import Connection
from modules.executors import SqlExecutor


class View:
    def __init__(
        self, title: str, id: str, load_all: bool = True, is_graph: bool = True
    ) -> None:
        self._children: list[html.H1 | html.Div | None] = []
        self._has_title = False
        if title != "":
            self._children.append(html.H1(title))
            self._has_title = True
        self._id = id

        self._sql_executor = SqlExecutor(
            database=Connection.DATABASE,
            user=Connection.USER,
            password=Connection.PASSWORD,
            host=Connection.HOST,
            port=Connection.PORT,
        )
        self._className_child = "card"
        self._className = "hide"
        if is_graph:
            self._className += " card_container"
        if load_all:
            self._load_all()

    def _load_all(self) -> None:
        pass

    def _remove_background(self, figure: "plotly.graph_objects.Figure") -> None:
        figure.update_layout(
            {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"}
        )

    def get_container(self) -> "html.Div":
        return html.Div(children=self._children, className=self._className, id=self._id)

    def get_children(self) -> list:
        return self._children

    def _get_selector(
        self,
        text: str | tuple[str, str],
        id: str,
        options: list[dict[str, Any]],
        value: str,
        className: str = "selector",
    ) -> "html.Div":
        if isinstance(text, tuple):
            return html.Div(
                [
                    html.H3(text[0]),
                    dbc.Select(
                        id=id, options=options, value=value, className=className
                    ),
                    html.H3(text[1]),
                ],
                className="inline_selector_container",
            )
        return html.Div(
            [
                html.H3(text),
                dbc.Select(id=id, options=options, value=value, className=className),
            ],
            className="inline_selector_container",
        )

    def _add_child(self, child) -> None:

        if isinstance(child, list):
            self._children.append(html.Div(child, className=self._className_child))
        else:
            self._children.append(child)

    def update_all(self) -> None:
        if self._has_title:
            self._children = [self._children[0]]
        else:
            self._children.clear()
        self._load_all()


class Introduction(View):
    def __init__(self, id: str, load_all: bool = True) -> None:
        super().__init__(
            """\
            Análisis de un conjunto de datos usando diagramas relacionales, \
            y de entidad-relación, base de datos PostgreSQL y Python\
        """,
            id,
            load_all,
            False,
        )
        self._className = "introduction"

    def _load_all(self) -> None:
        self.__add_description()

    def __add_description(self) -> None:
        self._add_child(
            [
                html.H2("Descripción"),
                html.P(
                    """\
                En el conjunto de datos nos presentan un esquema general \
                demográfico de una persona y cuántos colombianos emigrantes \
                pertenecen a esta. En nuestro análisis acordamos los siguientes \
                datos como variables de interés:\
                """
                ),
                HtmlTable(
                    ["Variable", "Descripción"],
                    rows=[
                        ["Edad", "Edad actual dada en años"],
                        ["Especialización", "Carrera que desempeña"],
                        [
                            "Área de conocimiento",
                            "Campo en el cual pertenece la especialización",
                        ],
                        ["Nivel académico", "El nivel educativo alcanzado"],
                        ["País de residencia", "País actual en el que vive"],
                        [
                            "Oficina de registro",
                            "Lugar en el cual está catalogado; masculino, femenino o desconocido",
                        ],
                        ["Estatura", "Altura en centímetros"],
                        [
                            "Cantidad de personas",
                            "La cantidad de personas que coinciden con la descripción demográfica",
                        ],
                    ],
                ).get_container(),
            ]
        )


class NumberPeopleView(View):
    NUMBER_CITIES = 10

    def __init__(self, title: str, id: str, load_all: bool = True) -> None:
        super().__init__(title, id, load_all)

    def _load_all(self) -> None:
        self.add_map_by_country()
        self.add_plot_by_city()

    def add_map_by_country(self) -> None:

        columns = ["cantidad personas", "codigo pais", "nombre pais"]

        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd."cantidad_personas") AS "{columns[0]}",
                ps.codigo as "{columns[1]}",
                ps.nombre as "{columns[2]}"
            FROM
                "DescripcionDemografica" AS dd
                JOIN
                "OficinaRegistro" AS ofr
                ON (ofr.id = dd."id_OficinaRegistro")
                JOIN
                "Pais" as ps
                ON (ps.id = ofr."id_Pais")
            GROUP BY 2, 3
            """,
            handle_conn=pd.read_sql_query,
        )

        df = pd.DataFrame(res, columns=columns)

        figure = px.choropleth(
            df,
            locations=columns[1],
            locationmode="ISO-3",
            color=columns[0],
            hover_name=columns[2],
            color_continuous_scale=px.colors.sequential.Mint,
        )

        self._remove_background(figure)

        self._add_child(
            [
                html.H3("Personas por país"),
                dcc.Graph(id="number_people_by_country", figure=figure),
            ]
        )

    def add_plot_by_city(self) -> None:
        columns = ["cantidad personas", "nombre ciudad"]

        res = self._sql_executor.run_query(
            f"""
                SELECT
                    SUM(dd."cantidad_personas") AS "{columns[0]}",
                    ofr.nombre as "{columns[1]}"
                FROM
                    "DescripcionDemografica" AS dd
                    JOIN
                    "OficinaRegistro" AS ofr
                    ON (ofr.id = dd."id_OficinaRegistro")
                GROUP BY 2
                ORDER BY 1 DESC
                LIMIT {NumberPeopleView.NUMBER_CITIES}
                """,
            handle_conn=pd.read_sql_query,
        )

        df = pd.DataFrame(res, columns=columns)

        bar = px.bar(df, x=columns[1], y=columns[0])
        pie = px.pie(df, names=columns[1], values=columns[0])

        self._remove_background(bar)
        self._remove_background(pie)

        self._add_child(
            [
                self._get_selector(
                    ("Las", "ciudades con mayor cantidad de personas"),
                    "number_cities_selector",
                    [{"label": x, "value": x} for x in range(5, 31)],
                    str(NumberPeopleView.NUMBER_CITIES),
                ),
                html.Div(
                    [
                        dcc.Graph(id="number_people_by_city_barplot", figure=bar),
                        dcc.Graph(id="number_people_by_city_pie", figure=pie),
                    ],
                    className="splited_cards",
                ),
            ]
        )


class SpecializationView(View):
    ACTUAL_SPECIALIZATION = ""

    def __init__(self, title: str, id: str, load_all: bool = True) -> None:
        super().__init__(title, id, load_all)

    def _load_all(self) -> None:
        self.add_plots_by_knowledge()
        self.add_map()

    def __custom_selector(self, text: str | tuple[str, str]) -> "html.Div":
        res = self._sql_executor.run_query(
            f"""
            SELECT
                DISTINCT(esp.nombre)
            FROM
                "Especializacion" as esp
                JOIN
                "AreaConocimiento" as ac
                ON (esp."id_AreaConocimiento" = ac.id)
            WHERE
                ac.nombre = '{KnowledgeAreaView.ACTUAL_KNOWLEDGE}'
            """
        )

        return self._get_selector(
            text,
            "specialization_selector",
            [{"label": name, "value": name} for name in res or []],
            SpecializationView.ACTUAL_SPECIALIZATION,
        )

    def add_plots_by_knowledge(self) -> None:
        columns = ["cantidad personas", "especialización", "género"]
        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd.cantidad_personas) as "{columns[0]}",
                esp.nombre as "{columns[1]}",
                g.nombre as "{columns[2]}"
            FROM
                "DescripcionDemografica" as dd
                JOIN
                "Especializacion" as esp
                ON (dd."id_Especializacion" = esp.id)
                JOIN
                "AreaConocimiento" as ac
                ON (esp."id_AreaConocimiento" = ac.id)
                JOIN
                "Genero" as g
                ON (g.id = dd."id_Genero")
            WHERE
                ac.nombre = '{KnowledgeAreaView.ACTUAL_KNOWLEDGE}'
            GROUP BY 2, 3
            ORDER BY 3 DESC
            """
        )

        df = pd.DataFrame(res, columns=columns)

        barplot = px.bar(
            df, x=columns[1], y=columns[0], color=columns[2], barmode="group"
        )

        pie = px.pie(df, names=columns[1], values=columns[0])

        self._remove_background(barplot)

        self._remove_background(pie)

        self._add_child(
            [
                html.H3("Cantidad de personas por especialización"),
                html.Div(
                    [
                        dcc.Graph(
                            id="number_people_by_specialization_barplot", figure=barplot
                        ),
                        dcc.Graph(id="number_people_by_specialization_pie", figure=pie),
                    ],
                    className="splited_cards",
                ),
            ]
        )

    def add_map(self) -> None:
        if SpecializationView.ACTUAL_SPECIALIZATION == "":
            self._add_child(
                [self.__custom_selector("Selecciona una especialización: ")]
            )
            return
        columns = ["numero personas", "pais", "codigo pais", "género"]
        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd.cantidad_personas) as "{columns[0]}",
                ps.nombre as "{columns[1]}",
                ps.codigo as "{columns[2]}",
                g.nombre as "{columns[3]}"
            FROM
                "DescripcionDemografica" as dd
                JOIN
                "OficinaRegistro" as ofr
                ON (dd."id_OficinaRegistro" = ofr.id)
                JOIN
                "Pais" as ps
                ON (ofr."id_Pais" = ps.id)
                JOIN
                "Especializacion" as esp
                ON (dd."id_Especializacion" = esp.id)
                JOIN
                "Genero" as g
                ON (g.id = dd."id_Genero")
            WHERE
                esp.nombre = '{SpecializationView.ACTUAL_SPECIALIZATION}'
            GROUP BY 2, 3, 4
            ORDER BY 4 DESC, 1 DESC
            """
        )

        df = pd.DataFrame(res, columns=columns)

        print(len(df.groupby(columns[3])))

        map = px.choropleth(
            df,
            locations=columns[2],
            locationmode="ISO-3",
            color=columns[0],
            hover_name=columns[1],
            color_continuous_scale=px.colors.sequential.Mint,
        )

        self._remove_background(map)
        maps: dict = {}
        for data in df.groupby(columns[3]):
            maps[data[0]] = px.choropleth(
                data[1],
                locations=columns[2],
                locationmode="ISO-3",
                color=columns[0],
                hover_name=columns[1],
                color_continuous_scale=px.colors.sequential.Mint,
            )
            self._remove_background(maps[data[0]])

        self._add_child(
            [
                self.__custom_selector("Popularidad especialización "),
                html.Div(
                    [
                        html.Div([html.H4(key), dcc.Graph(figure=value)])
                        for key, value in maps.items()
                    ],
                    className="splited_cards",
                ),
            ]
        )


class KnowledgeAreaView(View):
    ACTUAL_KNOWLEDGE = ""

    def __init__(self, title: str, id: str, load_all: bool = True) -> None:
        super().__init__(title, id, load_all)
        self.__esp_view = SpecializationView("", "specialization", False)

    def _load_all(self) -> None:
        self.add_barplot()
        self.add_plots_by_knowledge()

    def __custom_selector(self, text: str | tuple[str, str]) -> "html.Div":
        res = self._sql_executor.run_query(
            f"""
            SELECT
                distinct(nombre)
            FROM
                "AreaConocimiento"
        """
        )

        return self._get_selector(
            text,
            "knowledge_name_selector",
            [{"label": name, "value": name} for name in res or []],
            KnowledgeAreaView.ACTUAL_KNOWLEDGE,
        )

    def add_barplot(self) -> None:
        columns = ["cantidad personas", "área de conocimiento", "género"]

        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd.cantidad_personas) as "{columns[0]}",
                ac.nombre as "{columns[1]}",
                g.nombre as "{columns[2]}"
            FROM
                "AreaConocimiento" as ac
                JOIN
                "Especializacion" as esp
                ON (ac.id = esp."id_AreaConocimiento")
                JOIN
                "DescripcionDemografica" as dd
                ON (dd."id_Especializacion" = esp.id)
                JOIN
                "Genero" as g
                ON (g.id = dd."id_Genero")
            GROUP BY 2, 3
            ORDER BY 3 DESC, 1 DESC
            """,
            handle_conn=pd.read_sql_query,
        )

        df = pd.DataFrame(res, columns=columns)

        figure = px.bar(
            df, x=columns[1], y=columns[0], color=columns[2], barmode="group"
        )

        self._remove_background(figure)
        self._add_child(
            [
                html.H3("Cantidad de personas por área de conocimiento"),
                dcc.Graph(
                    id="knowledge_area_barplot",
                    figure=figure,
                ),
            ]
        )

    def add_plots_by_knowledge(self) -> None:
        if KnowledgeAreaView.ACTUAL_KNOWLEDGE == "":
            self._add_child(
                [
                    self.__custom_selector("Seleccione un área de conocimiento: "),
                    self._get_selector("", "specialization_selector", [], "", "hide"),
                ]
            )
            return

        columns = ["cantidad personas", "pais", "código pais"]

        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd.cantidad_personas) as "{columns[0]}",
                ps.nombre as "{columns[1]}",
                ps.codigo as "{columns[2]}"
            FROM
                "AreaConocimiento" as ac
                JOIN
                "Especializacion" as esp
                ON (ac.id = esp."id_AreaConocimiento")
                JOIN
                "DescripcionDemografica" as dd
                ON (dd."id_Especializacion" = esp.id)
                JOIN
                "OficinaRegistro" as ofr
                ON (ofr.id = dd."id_OficinaRegistro")
                JOIN
                "Pais" as ps
                ON (ps.id = ofr."id_Pais")
            WHERE
                ac.nombre = '{KnowledgeAreaView.ACTUAL_KNOWLEDGE}'
            GROUP BY 2, 3
            """,
            handle_conn=pd.read_sql_query,
        )

        df = pd.DataFrame(res, columns=columns)

        map = px.choropleth(
            df,
            locations=columns[2],
            locationmode="ISO-3",
            color=columns[0],
            hover_name=columns[1],
            color_continuous_scale=px.colors.sequential.Mint,
        )
        self._remove_background(map)

        columns = ["cantidad personas", "continente", "género"]

        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd.cantidad_personas) as "{columns[0]}",
                c.nombre as "{columns[1]}",
                g.nombre as "{columns[2]}"
            FROM
                "DescripcionDemografica" as dd
                JOIN
                "OficinaRegistro" as ofr
                ON (ofr.id = dd."id_OficinaRegistro")
                JOIN
                "Pais" as ps
                ON (ps.id = ofr."id_Pais")
                JOIN
                "Continente" as c
                ON (c.id = ps."id_Continente")
                JOIN
                "Especializacion" as esp
                ON (dd."id_Especializacion" = esp.id)
                JOIN
                "AreaConocimiento" as ac
                ON (esp."id_AreaConocimiento" = ac.id)
                JOIN
                "Genero" as g
                ON (g.id = dd."id_Genero")
            WHERE
                ac.nombre = '{KnowledgeAreaView.ACTUAL_KNOWLEDGE}'

            GROUP BY 2, 3
            ORDER BY 3 DESC
            """
        )

        df = pd.DataFrame(res, columns=columns)

        barplot = px.bar(
            df, x=columns[1], y=columns[0], color=columns[2], barmode="group"
        )

        self._remove_background(barplot)

        self.__esp_view.update_all()

        self._add_child(
            [
                self.__custom_selector("Popularidad área de conocimiento"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Por país"),
                                dcc.Graph(id="knowledge_area_by_country", figure=map),
                            ]
                        ),
                        html.Div(
                            [
                                html.H4("Por continente"),
                                dcc.Graph(
                                    id="knowledge_area_by_continent", figure=barplot
                                ),
                            ]
                        ),
                    ],
                    className="splited_cards",
                ),
                *self.__esp_view.get_children(),
            ]
        )

    def get_container(self) -> "html.Div":
        return super().get_container()


class AgeView(View):
    def __init__(self, title: str, id: str, load_all: bool = True) -> None:
        super().__init__(title, id, load_all)

    def _load_all(self) -> None:
        self.add_boxplot()
        self.add_barplot()

    def add_boxplot(self) -> None:
        columns = ["años persona"]

        res = self._sql_executor.run_query(
            f"""
            SELECT
                dd.edad as "{columns[0]}"
            FROM
                "DescripcionDemografica" as dd
            """,
            handle_conn=pd.read_sql_query,
        )

        df = pd.DataFrame(res, columns=columns)

        figure = px.box(df, y=columns[0])
        self._remove_background(figure)

        self._add_child(
            [
                html.H3("Años de una persona"),
                dcc.Graph(id="year_boxplot", figure=figure),
            ]
        )

    def add_barplot(self) -> None:
        columns = ["personas", "edad"]

        res = self._sql_executor.run_query(
            f"""
            SELECT
                SUM(dd.cantidad_personas) as "{columns[0]}",
                dd.edad as "{columns[1]}"
            FROM
                "DescripcionDemografica" as dd
            GROUP BY 2
            """,
            handle_conn=pd.read_sql_query,
        )

        df = pd.DataFrame(res, columns=columns)

        figure = px.bar(df, x=columns[1], y=columns[0])
        self._remove_background(figure)

        self._add_child(
            [
                html.H3("Cantidad de personas por edad"),
                dcc.Graph(
                    id="year_histplot",
                    figure=figure,
                ),
            ]
        )


class EducationLevelView(View):
    ACTUAL_CONTINENT = ""
    ACTUAL_EDUCATION = ""

    def __init__(self, title: str, id: str, load_all: bool = True) -> None:
        super().__init__(title, id, load_all)

    def _load_all(self) -> None:
        self.add_map()
        self.add_frequency_table()

    def add_map(self) -> None:
        res = (
            self._sql_executor.run_query(
                """
            SELECT
                DISTINCT(na.nombre)
            FROM
                "NivelAcademico" as na
            """
            )
            or []
        )

        self._add_child(
            [
                self._get_selector(
                    "Seleccione un nivel académico: ",
                    "education_selector",
                    [{"label": name.capitalize(), "value": name} for name, *_ in res],
                    EducationLevelView.ACTUAL_EDUCATION,
                )
            ]
        )

        if EducationLevelView.ACTUAL_EDUCATION == "":
            return

        columns = ["código país", "nombre país", "cantidad personas"]
        res = self._sql_executor.run_query(
            f"""
            SELECT
                ps.codigo as "{columns[0]}",
                ps.nombre as "{columns[1]}",
                SUM(dd.cantidad_personas) as "{columns[2]}"
            FROM
                "DescripcionDemografica" as dd
                JOIN
                "OficinaRegistro" as ofr
                ON (dd."id_OficinaRegistro" = ofr.id)
                JOIN
                "Pais" as ps
                ON (ps.id = ofr."id_Pais")
                JOIN
                "NivelAcademico" as na
                ON (na.id = dd."id_NivelAcademico")
            WHERE
                na.nombre = '{EducationLevelView.ACTUAL_EDUCATION}'
            GROUP BY
                1, 2
            """
        )

        df = pd.DataFrame(res, columns=columns)

        map = px.choropleth(
            df,
            locations=columns[0],
            locationmode="ISO-3",
            color=columns[2],
            hover_name=columns[1],
            color_continuous_scale=px.colors.sequential.Mint,
        )

        self._remove_background(map)

        self._add_child(
            [
                html.H3(
                    f"Nivel académico {EducationLevelView.ACTUAL_EDUCATION} por país"
                ),
                dcc.Graph(figure=map),
            ]
        )

    def add_frequency_table(self) -> None:
        res = self._sql_executor.run_query(
            """
            SELECT
                DISTINCT(c.nombre) 
            FROM
                "Continente" as c
            """
        )
        self._add_child(
            [
                self._get_selector(
                    "Seleccione un continente:",
                    "continent_selector",
                    [
                        {"label": nombre.capitalize(), "value": nombre}
                        for nombre, *_ in res or []
                    ],
                    EducationLevelView.ACTUAL_CONTINENT,
                )
            ]
        )

        if EducationLevelView.ACTUAL_CONTINENT == "":
            return
        columns = ["nivel académico", "frecuencia"]
        res = (
            self._sql_executor.run_query(
                f"""
            SELECT
                na.nombre as "{columns[1]}",
                SUM(dd.cantidad_personas) as "{columns[0]}"
            FROM
                "DescripcionDemografica" as dd
                JOIN
                "NivelAcademico" as na
                ON (na.id = dd."id_NivelAcademico")
                JOIN
                "OficinaRegistro" as ofr
                ON (ofr.id = dd."id_OficinaRegistro")
                JOIN
                "Pais" as ps
                ON (ps.id = ofr."id_Pais")
                JOIN 
                "Continente" as c
                ON (c.id = ps."id_Continente")
            WHERE
                c.nombre = '{EducationLevelView.ACTUAL_CONTINENT}'
            GROUP BY
                1
            ORDER BY
                2 DESC
            """
            )
            or []
        )

        res = [[name.capitalize(), int(frequency)] for name, frequency in res]
        df = pd.DataFrame(res, columns=columns)

        bar = px.bar(df, x=columns[0], y=columns[1])

        pie = px.pie(df, names=columns[0], values=columns[1])

        self._remove_background(pie)

        self._remove_background(bar)

        length = sum([frequency for _, frequency in res])

        table_columns = [
            *columns,
            "frecuencia acumulada",
            "frecuencia relativa",
            "porcentaje",
            "acumulado",
        ]

        res = [
            [
                name,
                frequency,
                0,
                round(frequency / length, 3),
                f"{round(frequency / length * 100, 3)}%",
            ]
            for name, frequency in res
        ]

        acum = 0
        for i, el in enumerate(res):
            acum += float(el[1] / length * 100)
            res[i][2] = el[1] if i == 0 else (res[i - 1][2] + el[1])
            res[i].append(f"{round(acum, 3)}%")

        self._add_child(
            [
                HtmlTable(
                    headers=table_columns,
                    rows=res,
                ).get_container(),
            ]
        )

        self._add_child(
            [
                html.Div(
                    [dcc.Graph(figure=bar), dcc.Graph(figure=pie)],
                    className="splited_cards",
                )
            ]
        )
