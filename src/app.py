#!/usr/bin/env python3.10

from ast import Num
import dash_bootstrap_components as dbc
from contextlib import suppress
from dash import Dash, html, Output, Input, dcc
from modules.components import Sidebar
from modules.views import (
    EducationLevelView,
    Introduction,
    NumberPeopleView,
    KnowledgeAreaView,
    AgeView,
    SpecializationView,
)
from settings import Files, Server
from modules.utils import data_insertion, initialize_tables, prepare_files


with suppress(Exception):
    prepare_files()
    initialize_tables()
    data_insertion()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME],
    title="Emigrantes colombianos",
    assets_folder=Files.PATH,
)


class StaticElements:
    INTRODUCTION = Introduction("es_introduction")
    NUMBER_PEOPLE_VIEW = NumberPeopleView(
        title="Vista número de personas", id="number_people"
    )
    KNOWLEDGE_AREA_VIEW = KnowledgeAreaView(
        title="Vista área de conocimientos", id="knowledge_area"
    )
    AGE_VIEW = AgeView(title="Vista de edad de una persona", id="age_person")
    EDUCATION_LEVEL_VIEW = EducationLevelView(
        "Vista del nivel académico", id="education_level"
    )


def main():
    sidebar = Sidebar(
        "Emigrantes colombianos", "Aquí encontrarás todas las gráficas posibles"
    )
    sidebar.add_link("Inicio", "#", className="active")
    sidebar.add_link("Número de personas", "#number_people")
    sidebar.add_link("Areas de conocimiento", "#knowledge_area")
    sidebar.add_link("Años de las personas", "#age_person")
    sidebar.add_link("Nivel académico", "#education_level")

    nav_slider_button = dbc.Button(
        [html.I(className="fa-solid fa-bars")], id="slider_btn"
    )
    content = html.Div(
        [
            StaticElements.INTRODUCTION.get_container(),
            StaticElements.NUMBER_PEOPLE_VIEW.get_container(),
            StaticElements.KNOWLEDGE_AREA_VIEW.get_container(),
            StaticElements.AGE_VIEW.get_container(),
            StaticElements.EDUCATION_LEVEL_VIEW.get_container(),
            nav_slider_button,
        ],
        id="page_content",
    )

    app.layout = html.Div(
        [
            dbc.Input(id="hide_loader", type="hidden"),
            dcc.Location(id="url", href="/#"),
            sidebar.get_container(),
            dcc.Loading(content, fullscreen=True, type="circle", id="content_loader"),
        ],
        id="content",
    )

    app.run_server(port=Server.PORT, host=Server.HOST, debug=True)


@app.callback(
    Output("knowledge_area", "children"),
    [
        Input("knowledge_name_selector", "value"),
        Input("specialization_selector", "value"),
    ],
)
def change_current_knowledge_name(knowledge_name, specialization) -> "html.Div":
    if KnowledgeAreaView.ACTUAL_KNOWLEDGE != knowledge_name:
        KnowledgeAreaView.ACTUAL_KNOWLEDGE = knowledge_name
        SpecializationView.ACTUAL_SPECIALIZATION = ""
        StaticElements.KNOWLEDGE_AREA_VIEW.update_all()
    elif SpecializationView.ACTUAL_SPECIALIZATION != specialization:
        SpecializationView.ACTUAL_SPECIALIZATION = specialization
        StaticElements.KNOWLEDGE_AREA_VIEW.update_all()
    return html.Div(StaticElements.KNOWLEDGE_AREA_VIEW.get_children())


@app.callback(Output("content_loader", "fullscreen"), Input("hide_loader", "value"))
def disable_fullscreen_loader(_):
    return False


@app.callback(
    Output("number_people", "children"), [Input("number_cities_selector", "value")]
)
def update_number_cities_displayed(number_cities) -> "html.Div":
    if NumberPeopleView.NUMBER_CITIES != number_cities:
        NumberPeopleView.NUMBER_CITIES = number_cities
        StaticElements.NUMBER_PEOPLE_VIEW.update_all()
    return html.Div(StaticElements.NUMBER_PEOPLE_VIEW.get_children())


@app.callback(
    Output("education_level", "children"),
    [Input("continent_selector", "value"), Input("education_selector", "value")],
)
def show_frequency_table(continent, education) -> "html.Div":
    changed = False
    if EducationLevelView.ACTUAL_CONTINENT != continent:
        EducationLevelView.ACTUAL_CONTINENT = continent
        changed = True
    if EducationLevelView.ACTUAL_EDUCATION != education:
        EducationLevelView.ACTUAL_EDUCATION = education
        changed = True

    if changed:
        StaticElements.EDUCATION_LEVEL_VIEW.update_all()
    return html.Div(StaticElements.EDUCATION_LEVEL_VIEW.get_children())


if __name__ == "__main__":
    main()
