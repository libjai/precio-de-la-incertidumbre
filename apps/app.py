#!/usr/bin/env python3
"""Hub de los dashboards del libro 'El Precio de la Incertidumbre'.
Ejecuta:  streamlit run apps/app.py
Portada + navegación entre el explorador de griegas (Cap. 6) y la valuación con tres
motores (Cap. 11). Cada dashboard también corre por separado."""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import componentes as ui
import dashboard_griegas
import dashboard_valuacion

st.set_page_config(page_title=f"{ui.LIBRO['titulo']} · Dashboards", page_icon="📈", layout="wide")


def inicio() -> None:
    ui.portada(PAGINAS_NAV)


PAGINAS_NAV = [
    st.Page(dashboard_griegas.render, title="Griegas · Cap. 6", icon="📐", url_path="griegas"),
    st.Page(dashboard_valuacion.render, title="Valuación · Cap. 11", icon="⚖️", url_path="valuacion"),
]
pg = st.navigation({ui.LIBRO["titulo"]: [st.Page(inicio, title="Inicio", icon="📖", default=True),
                                         *PAGINAS_NAV]})
ui.barra_lateral(hub=True)
pg.run()
