"""Componentes Streamlit compartidos: identidad del libro, selector de tema y paneles.

Todo dashboard del repo lleva la marca del libro (encabezado, tarjeta lateral, pie) para
que el lector tenga presente que el material es parte de *El Precio de la Incertidumbre*
y que cada vista remite a un capítulo."""
import streamlit as st
from streamlit import config as _cfg

import graficos as gf
from tema import MODOS, paleta

LIBRO = {
    "titulo": "El Precio de la Incertidumbre",
    "subtitulo": "Valuación de opciones con Python",
    "autor": "Liber Jaime Merlos",
    "edicion": "Primera edición · 2026",
    "repo": "https://github.com/libjai/precio-de-la-incertidumbre",
    "autor_url": "https://github.com/libjai",
}

PAGINAS = {
    "griegas": {"titulo": "Explorador de griegas", "capitulo": "Cap. 6",
                "icono": "📐", "archivo": "apps/dashboard_griegas.py",
                "resumen": "P&L con cono de ±1σ, escaleras de griegas por vencimiento, pares del "
                           "analista, matriz de sensibilidad y cadena de opciones (BSM)."},
    "valuacion": {"titulo": "Valuación con tres motores", "capitulo": "Cap. 11",
                  "icono": "⚖️", "archivo": "apps/dashboard_valuacion.py",
                  "resumen": "BSM, binomial CRR y Longstaff-Schwartz sobre una opción estilo MexDer: "
                             "frontera de ejercicio, convergencia, mapas de precio y sonrisa de vol."},
}

# Cálculos con caché: al mover un parámetro solo se recalcula lo que cambió.
curvas_griegas = st.cache_data(show_spinner=False)(gf.curvas_griegas)
escaleras_griegas = st.cache_data(show_spinner=False)(gf.escaleras_griegas)
payoff_y_valor = st.cache_data(show_spinner=False)(gf.payoff_y_valor)
cadena_opciones = st.cache_data(show_spinner=False)(gf.cadena_opciones)
matriz_sensibilidad = st.cache_data(show_spinner=False)(gf.matriz_sensibilidad)
frontera_ejercicio = st.cache_data(show_spinner=False)(gf.frontera_ejercicio)
convergencia_crr = st.cache_data(show_spinner=False)(gf.convergencia_crr)
convergencia_lsm = st.cache_data(show_spinner="Simulando Longstaff-Schwartz…")(gf.convergencia_lsm)
mapa_americano = st.cache_data(show_spinner="Valuando árboles binomiales…")(gf.mapa_americano)
mapa_sigma_r = st.cache_data(show_spinner="Valuando con el motor elegido…")(gf.mapa_sigma_r)
mapa_vol_implicita = st.cache_data(show_spinner=False)(gf.mapa_vol_implicita)
mapa_tasa_implicita = st.cache_data(show_spinner=False)(gf.mapa_tasa_implicita)


# --------------------------------------------------------------------------------- tema

def modo_actual() -> str:
    """Fuente de verdad del tema: la configuración que el servidor está sirviendo. Así el
    primer render y las figuras coinciden con lo que el navegador muestra."""
    if "modo_tema" not in st.session_state:
        base = str(_cfg.get_option("theme.base") or "dark").lower()
        st.session_state["modo_tema"] = "light" if base == "light" else "dark"
    return st.session_state["modo_tema"]


def _aplicar_tema_streamlit(modo: str) -> None:
    for k, v in MODOS[modo]["streamlit"].items():
        _cfg.set_option(f"theme.{k}", v)


def selector_tema() -> str:
    modo = modo_actual()
    etiquetas = {"dark": "🌙 Oscuro", "light": "☀️ Claro"}
    elegido = st.segmented_control("Tema", list(etiquetas), default=modo,
                                   format_func=etiquetas.get, key="selector_tema")
    if elegido and elegido != modo:
        st.session_state["modo_tema"] = elegido
        _aplicar_tema_streamlit(elegido)
        st.rerun()
    return modo


# -------------------------------------------------------------------------------- marca

def _tarjeta_libro(c) -> str:
    return f"""
<div style="border-left:3px solid {c['acento']}; padding:.35rem .8rem; margin:.2rem 0 .6rem;">
  <div style="font-size:.68rem; letter-spacing:.14em; text-transform:uppercase; color:{c['apagada']};">Libro</div>
  <div style="font-size:1.05rem; font-weight:700; line-height:1.2; color:{c['tinta']};">{LIBRO['titulo']}</div>
  <div style="font-size:.85rem; color:{c['secundaria']};">{LIBRO['subtitulo']}</div>
  <div style="font-size:.78rem; color:{c['apagada']}; margin-top:.35rem;">{LIBRO['autor']} · {LIBRO['edicion']}</div>
</div>"""


def barra_lateral(pagina: str | None = None, hub: bool = False) -> None:
    c = paleta(modo_actual())["chrome"]
    with st.sidebar:
        st.html(_tarjeta_libro(c))
        selector_tema()
        st.link_button("Código del libro en GitHub", LIBRO["repo"], icon="💻", width="stretch")
        if not hub:
            otras = [k for k in PAGINAS if k != pagina]
            if otras:
                st.caption("Todo está ligado. El otro dashboard del libro:")
                for k in otras:
                    q = PAGINAS[k]
                    st.markdown(f"{q['icono']} **{q['titulo']}** · {q['capitulo']}  \n"
                                f"`streamlit run {q['archivo']}`")
                st.caption("O abre ambos desde el hub: `streamlit run apps/app.py`")
        st.divider()


def encabezado(pagina: str, idea: str) -> None:
    q = PAGINAS[pagina]
    c = paleta(modo_actual())["chrome"]
    st.html(f"""
<div style="display:flex; align-items:center; gap:.6rem; flex-wrap:wrap; margin-bottom:.1rem;">
  <span style="font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; font-weight:600; color:{c['acento']};">{LIBRO['titulo']}</span>
  <span style="color:{c['apagada']};">·</span>
  <span style="font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; color:{c['apagada']};">{q['capitulo']} · dashboard</span>
</div>
<h1 style="margin:0 0 .4rem 0; font-size:1.9rem; line-height:1.15; color:{c['tinta']};">{q['icono']} {q['titulo']}</h1>
<p style="margin:0 0 1rem 0; font-size:.95rem; max-width:62rem; color:{c['secundaria']};">
  <b style="color:{c['tinta']};">Idea principal:</b> {idea}
</p>""")


def pie(pagina: str) -> None:
    otra = next(q for k, q in PAGINAS.items() if k != pagina)
    st.divider()
    st.caption(
        f"Material del libro **{LIBRO['titulo']}: {LIBRO['subtitulo']}** "
        f"({LIBRO['autor']}, {LIBRO['edicion']}). Código bajo licencia MIT en "
        f"[GitHub]({LIBRO['repo']}). Material educativo; no es asesoría de inversión. "
        f"Continúa en {otra['icono']} **{otra['titulo']}** ({otra['capitulo']})."
    )


def portada(paginas_nav) -> None:
    """Portada del hub (apps/app.py)."""
    c = paleta(modo_actual())["chrome"]
    st.html(f"""
<div style="font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; font-weight:600; color:{c['acento']};">Dashboards del libro</div>
<h1 style="margin:0 0 .2rem 0; font-size:2.3rem; line-height:1.1; color:{c['tinta']};">{LIBRO['titulo']}</h1>
<p style="margin:0 0 1.2rem 0; font-size:1.05rem; color:{c['secundaria']};">{LIBRO['subtitulo']} · {LIBRO['autor']}</p>""")
    st.markdown(
        "Los dashboards son la versión interactiva de las tablas y figuras del libro: "
        "los mismos motores de `opciones.py`, los mismos parámetros que declaras en cada "
        "capítulo, pero en vivo y con las vistas que usan las mesas de opciones: P&L con "
        "cono de ±1σ, escaleras de griegas, cadena, frontera de ejercicio y sonrisa de vol. "
        "Volatilidad y tasa se expresan en % anual, como en el mercado."
    )
    cols = st.columns(len(PAGINAS))
    for col, (k, q), pg in zip(cols, PAGINAS.items(), paginas_nav):
        with col.container(border=True):
            st.markdown(f"### {q['icono']} {q['titulo']}")
            st.caption(q["capitulo"])
            st.write(q["resumen"])
            st.page_link(pg, label=f"Abrir {q['titulo'].lower()}", icon="➡️")
    st.markdown(
        f"**Cómo se relaciona con el libro.** El libro muestra conceptos, fragmentos y "
        f"resultados; el código completo vive en el [repositorio]({LIBRO['repo']}). "
        f"Reproduce cada figura con `python ejemplos/capNN_*.py`."
    )


# ------------------------------------------------------------------------------ paneles

def nota(texto: str) -> None:
    c = paleta(modo_actual())["chrome"]
    with st.container(border=True):
        st.html(f"<div style='font-size:.68rem; letter-spacing:.14em; text-transform:uppercase; "
                f"color:{c['apagada']}; margin-bottom:.2rem;'>Cómo leer</div>")
        st.markdown(texto)


def grafico_con_nota(fig, texto: str) -> None:
    """Figura a la izquierda y recuadro 'Cómo leer' a la derecha (se apilan en pantallas
    angostas). La nota dice qué se ve, cómo leerlo y en qué unidades."""
    col_fig, col_nota = st.columns([2.3, 1], vertical_alignment="top")
    col_fig.pyplot(fig, width="stretch")
    with col_nota:
        nota(texto)


def panel_pares_griegas(modo: str, S, K, r, sig, T, tipo) -> None:
    """Gamma, vega y theta contra delta: los pares que mira un analista de opciones."""
    _, curvas = curvas_griegas(K, r, sig, T)
    actual = gf.griegas_actuales(S, K, r, sig, T, tipo)
    st.pyplot(gf.fig_pares_griegas(modo, curvas, actual, tipo), width="stretch")
    nota(
        "El eje x es delta, que funciona como *moneyness*: 0 es muy fuera del dinero, ±1 muy "
        "dentro (call positivo, put negativo). Cada panel recorre el spot de 0.4K a 1.8K con tus "
        "σ, r y T. **Gamma** (cambio de delta por 1 unidad de spot) y **vega** (cambio de precio "
        "por 1 punto de vol) son máximas cerca de |Δ| ≈ 0.5, en el dinero. **Theta** (cambio de "
        "precio por día calendario) es más negativa ahí: la opción que más se mueve es la que más "
        "cuesta sostener. El punto es tu opción; la curva tenue, la contraria (Cap. 6)."
    )
