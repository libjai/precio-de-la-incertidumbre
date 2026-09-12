"""Componentes Streamlit compartidos: identidad del libro, selector de tema, glosario,
lote/posición y paneles.

Todo dashboard del repo lleva la marca del libro (encabezado, tarjeta lateral, pie) para
que el lector tenga presente que el material es parte de *El Precio de la Incertidumbre*
y que cada vista remite a un capítulo. El lector objetivo es un estudiante que se acerca
por primera vez a la práctica de una mesa de opciones: cada término se explica."""
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

# Convención MexDer: cada contrato de opción sobre acciones ampara 100 acciones y no se
# operan fracciones de contrato (Condiciones Generales de Contratación, MexDer).
LOTE = 100
MONEDA = "MXN"

PAGINAS = {
    "griegas": {"titulo": "Explorador de griegas", "capitulo": "Cap. 6",
                "icono": "📐", "archivo": "apps/dashboard_griegas.py",
                "resumen": "P&L con cono de ±1σ, escaleras de griegas por vencimiento, pares del "
                           "analista, matriz de sensibilidad y cadena de opciones (BSM), por acción, "
                           "por contrato de 100 acciones y por posición."},
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
        f"Las cifras se muestran por acción y por contrato de {LOTE} acciones, como se opera "
        "en MexDer, y la volatilidad y la tasa van en % anual, como en el mercado. Si es tu "
        "primera vez, abre el **Glosario para empezar** en la barra lateral de cada dashboard."
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


# ------------------------------------------------------------------- glosario y posición

GLOSARIO = [
    ("Spot (S)", "precio actual del subyacente, la acción. En pesos."),
    ("Strike (K)", "precio de ejercicio: al que la opción te permite comprar (call) o vender (put)."),
    ("Prima", "lo que cuesta la opción. Se cotiza **por acción**; el contrato cuesta prima × 100."),
    ("T", "tiempo que falta al vencimiento, **en años**. T = 0.5 son seis meses (≈ 182 días); "
          "T/2 es la mitad del plazo y T/4 la cuarta parte. En una mesa se habla de 'días al vencimiento' (DTE)."),
    ("Volatilidad (σ)", "cuánto se mueve el subyacente, en % anual. 25 % significa que un movimiento "
                        "'normal' de un año es de ±25 %. Es el único parámetro que no se observa: se estima o se implica."),
    ("Tasa (r)", "tasa libre de riesgo anual, en %, con capitalización continua. En México la referencia es la TIIE o los Cetes."),
    ("Call / Put", "call: derecho a comprar a K. Put: derecho a vender a K. Ambos se pagan hoy y se ejercen después."),
    ("Europea / Americana", "la europea solo se ejerce al vencimiento; la americana en cualquier momento. "
                            "Las opciones sobre acciones de MexDer son americanas."),
    ("ITM / ATM / OTM", "dentro del dinero (ya conviene ejercer), en el dinero (S ≈ K) y fuera del dinero. "
                        "El grado se llama *moneyness*; delta funciona como su termómetro."),
    ("Contrato (lote)", f"unidad mínima de operación. En MexDer un contrato de opción sobre acciones ampara "
                        f"**{LOTE} acciones**; no se operan fracciones. Toda cifra por acción se multiplica por {LOTE}."),
    ("Posición", "número de contratos que compras (largo) o vendes (corto). Aquí siempre se muestra una posición larga."),
    ("Griegas", "sensibilidades del precio. Están en **pesos por acción**, no en porcentaje: cuánto cambia la prima "
                "si cambia el spot (delta), la propia delta (gamma), la vol (vega, por 1 punto porcentual), el tiempo "
                "(theta, por día) o la tasa (rho, por 1 punto porcentual)."),
    ("Punto porcentual (pp) vs. punto base (pb)", "1 pp es pasar de 25 % a 26 %. 1 pb es la centésima parte: de 25.00 % "
                "a 25.01 %. Aquí vega y rho van **por 1 pp**; en mesas de tasas es común verlas por pb (divide entre 100)."),
    ("Vol implícita", "la σ que hace que BSM reproduzca un precio de mercado. Es la 'temperatura' que cotiza el mercado."),
    ("P&L", "ganancia o pérdida (*profit and loss*) de la posición respecto a la prima pagada."),
    ("BSM / CRR / LSM", "los tres motores del libro: Black-Scholes-Merton (fórmula, europea), árbol binomial de "
                        "Cox-Ross-Rubinstein y Longstaff-Schwartz (Monte Carlo con regresión), ambos para americanas."),
]


def glosario() -> None:
    with st.sidebar.expander("📖 Glosario para empezar", expanded=False):
        for termino, texto in GLOSARIO:
            st.markdown(f"**{termino}.** {texto}")


def parametros_posicion() -> int:
    """Entrada del número de contratos (posición larga)."""
    with st.sidebar:
        st.header("Posición")
        contratos = st.number_input(f"Contratos (1 contrato = {LOTE} acciones)", min_value=1,
                                    max_value=10_000, value=1, step=1, key="pos_contratos",
                                    help=f"Convención MexDer para opciones sobre acciones: cada contrato "
                                         f"ampara {LOTE} acciones y no se operan fracciones de contrato.")
    return int(contratos)


def fila_posicion(act: dict, contratos: int) -> None:
    """Prima y griegas del contrato y de la posición, en pesos."""
    n = LOTE * contratos
    st.markdown(f"**Por contrato ({LOTE} acciones) y por posición ({contratos} contrato"
                f"{'s' if contratos != 1 else ''} = {n:,} acciones)**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Prima por contrato ({MONEDA})", f"{act['price'] * LOTE:,.2f}", border=True,
              help=f"Prima por acción × {LOTE}. Es lo que pagas por un contrato.")
    c1.metric(f"Prima de la posición ({MONEDA})", f"{act['price'] * n:,.2f}", border=True)
    c2.metric("Delta de la posición (acciones equivalentes)", f"{act['delta'] * n:,.1f}", border=True,
              help="Δ × acciones. La posición se mueve como si tuvieras esa cantidad de acciones; "
                   "es lo que un operador compra o vende para cubrirse (delta hedging).")
    c2.metric("Gamma de la posición (acciones por 1 MXN de spot)", f"{act['gamma'] * n:,.2f}", border=True,
              help="Cuántas acciones equivalentes gana o pierde la posición si el spot sube 1 peso.")
    c3.metric(f"Vega de la posición ({MONEDA} por 1 pp de vol)", f"{act['vega'] * n:,.2f}", border=True,
              help="Pesos que gana la posición si la volatilidad sube 1 punto porcentual "
                   "(p. ej. de 25 % a 26 %). No es por punto base.")
    c3.metric(f"Theta de la posición ({MONEDA} por día)", f"{act['theta'] * n:,.2f}", border=True,
              help="Pesos que pierde la posición cada día calendario que pasa, sin que nada más cambie.")
    c4.metric(f"Rho de la posición ({MONEDA} por 1 pp de tasa)", f"{act['rho'] * n:,.2f}", border=True,
              help="Pesos que cambia la posición si la tasa sube 1 punto porcentual.")


def nota_unidades_griegas() -> None:
    with st.expander("¿En qué unidades están las griegas? (léelo una vez)"):
        st.markdown(
            f"Las griegas de arriba son **cantidades de dinero por acción**, no porcentajes. "
            f"Si la acción cotiza en pesos, están en pesos por acción.\n\n"
            "- **Delta (Δ)**: pesos que cambia la prima por cada peso que sube el spot. Como es "
            "peso/peso, también se lee como fracción de acción: Δ = 0.6 significa que la opción "
            "se comporta como 0.6 acciones.\n"
            "- **Gamma (Γ)**: cuánto cambia delta si el spot sube 1 peso.\n"
            "- **Vega (ν)**: pesos que cambia la prima si la volatilidad sube **1 punto porcentual** "
            "(de 25 % a 26 %).\n"
            "- **Theta (Θ)**: pesos que pierde la prima por **cada día calendario** que pasa. Es "
            "negativa para quien compra la opción.\n"
            "- **Rho (ρ)**: pesos que cambia la prima si la tasa sube 1 punto porcentual.\n\n"
            f"Para pasar a **dinero del contrato**, multiplica por {LOTE} acciones; para la "
            "**posición**, por 100 × número de contratos. Eso es lo que muestra la fila de abajo. "
            "En las mesas se habla de 'dollar delta' o 'delta en pesos' para referirse a esas "
            "cifras agregadas."
        )


def selector_escala(contratos: int, key: str) -> tuple[float, str]:
    """Escala del P&L: por acción, por contrato o por posición. Devuelve (factor, etiqueta)."""
    opciones = {"accion": "Por acción", "contrato": f"Por contrato ({LOTE} acc.)",
                "posicion": f"Por posición ({contratos} contr.)"}
    e = st.segmented_control("Escala del P&L", list(opciones), default="contrato",
                             format_func=opciones.get, key=key) or "contrato"
    factor = {"accion": 1, "contrato": LOTE, "posicion": LOTE * contratos}[e]
    return factor, opciones[e]


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
        "**Qué ves:** tres relaciones entre griegas que un operador tiene en la cabeza. El eje x "
        "es delta, que funciona como termómetro de *moneyness*: 0 es muy fuera del dinero, ±1 muy "
        "dentro (call positivo, put negativo). Cada panel recorre el spot de 0.4K a 1.8K con tus "
        "σ, r y T.\n\n"
        "**Cómo leerlo:** **gamma** (cambio de delta por 1 peso de spot) y **vega** (pesos por 1 "
        "punto de vol) son máximas cerca de |Δ| ≈ 0.5, en el dinero. **Theta** (pesos por día) es "
        "más negativa ahí: la opción que más se mueve es la que más cuesta sostener. El punto es "
        "tu opción; la curva tenue, la contraria (Cap. 6).\n\n"
        f"**Unidades:** pesos por acción; multiplica por {LOTE} para el contrato."
    )
