#!/usr/bin/env python3
"""Dashboard interactivo de griegas — libro 'El Precio de la Incertidumbre' (Cap. 6).
Ejecuta:  streamlit run apps/dashboard_griegas.py   (o el hub: streamlit run apps/app.py)
Las vistas de una mesa de opciones sobre una opción europea (BSM): P&L con cono de ±1σ,
curva vs. spot, escaleras de griegas por vencimiento, pares del analista, matriz de
sensibilidad y cadena de opciones.
Unidades de mercado: vol y tasa en % anual; vega y rho por 1 punto; theta por día."""
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import componentes as ui
import graficos as gf
from tema import color_tipo


def render() -> None:
    modo = ui.modo_actual()
    ui.encabezado("griegas",
                  "las griegas son las derivadas del precio: dicen cuánto cambia y por qué. "
                  "Mueve un parámetro y observa cómo responden todas a la vez.")

    with st.sidebar:
        st.header("Parámetros")
        S = st.slider("Spot S", 10.0, 200.0, 100.0, 1.0, key="g_S")
        K = st.slider("Strike K", 10.0, 200.0, 100.0, 1.0, key="g_K")
        sig = st.slider("Volatilidad σ (% anual)", 1.0, 100.0, 25.0, 1.0, key="g_sig") / 100
        r = st.slider("Tasa r (% anual, continua)", 0.0, 20.0, 5.0, 0.25, key="g_r") / 100
        T = st.slider("Vencimiento T (años)", 0.05, 3.0, 1.0, 0.05, key="g_T")
        tipo = st.radio("Tipo", ["call", "put"], horizontal=True, key="g_tipo")
        comparar = st.toggle("Mostrar la opción contraria", value=True, key="g_comparar")

    act = gf.griegas_actuales(S, K, r, sig, T, tipo)
    c1, c2, c3 = st.columns(3)
    c1.metric("Precio", f"{act['price']:.4f}", border=True)
    c1.metric("Delta Δ", f"{act['delta']:.4f}", border=True,
              help="Cambio del precio por 1 unidad de spot.")
    c2.metric("Gamma Γ", f"{act['gamma']:.5f}", border=True,
              help="Cambio de delta por 1 unidad de spot.")
    c2.metric("Vega ν (por 1 pt de vol)", f"{act['vega']:.4f}", border=True,
              help="Cambio del precio si σ sube 1 punto porcentual (p. ej. de 25 % a 26 %).")
    c3.metric("Theta Θ (por día)", f"{act['theta']:.4f}", border=True,
              help="Cambio del precio por un día calendario (Θ anual / 365), la convención de mesa.")
    c3.metric("Rho ρ (por 1 pt de tasa)", f"{act['rho']:.4f}", border=True,
              help="Cambio del precio si r sube 1 punto porcentual.")

    tab_pl, tab_curva, tab_escalera, tab_pares, tab_matriz, tab_cadena = st.tabs(
        ["P&L y valor", "Curva vs. spot", "Escaleras por vencimiento", "Pares del analista",
         "Matriz de sensibilidad", "Cadena de opciones"])

    with tab_pl:
        lect = gf.lectura_mercado(S, K, r, sig, T, tipo)
        m1, m2, m3 = st.columns(3)
        m1.metric("Prob. de terminar dentro del dinero", f"{lect['p_itm'] * 100:.1f} %", border=True,
                  help="Probabilidad riesgo-neutral N(d₂) (call) o N(−d₂) (put). No es una "
                       "probabilidad 'real': descuenta la prima de riesgo.")
        m2.metric("Movimiento esperado ±1σ al vencimiento", f"± {lect['mov_1s']:.2f}", border=True,
                  help=f"S·σ·√T. Rango aproximado {lect['S_lo']:.2f} – {lect['S_hi']:.2f} "
                       "(≈ 68 % de los escenarios bajo el modelo).")
        m3.metric("Punto de equilibrio al vencimiento", f"{lect['equilibrio']:.2f}", border=True,
                  help="K + prima (call) o K − prima (put), comprando al precio BSM.")
        d = ui.payoff_y_valor(S, K, r, sig, T, tipo)
        ui.grafico_con_nota(
            gf.fig_payoff(modo, d, S, K, T, tipo, lect),
            f"**Qué ves:** la ganancia o pérdida por unidad de un {tipo} largo comprado hoy a "
            f"{d['prima']:.4f}, para cada nivel del subyacente. Tres momentos: al vencimiento "
            "(la línea quebrada, con zonas verde y roja), a mitad de camino (tenue) y hoy "
            "(la curva suave). Es la pantalla de escenarios de cualquier plataforma de opciones.\n\n"
            "**Cómo leerlo:** eje x = spot al evaluar, eje y = P&L. La banda sombreada es el "
            "rango de ±1σ del subyacente al vencimiento: lo que el mercado considera 'normal'. "
            "La distancia entre la curva de hoy y la del vencimiento es el valor tiempo que "
            "theta irá consumiendo.\n\n"
            "**Unidades:** P&L en unidades del subyacente, por opción.")

    with tab_curva:
        metrica = st.segmented_control("Métrica", ["price", "delta", "gamma", "vega", "theta"],
                                       default="price", format_func=gf.GRIEGAS.get,
                                       key="g_metrica") or "price"
        Sx = gf.rango_spot(K)
        y = gf.curva_metrica(Sx, K, r, sig, T, tipo, metrica)
        otro = "put" if tipo == "call" else "call"
        y_otro = gf.curva_metrica(Sx, K, r, sig, T, otro, metrica) if comparar else None
        ui.grafico_con_nota(
            gf.fig_curva_spot(modo, Sx, y, tipo, y_otro, S, act[metrica], K, metrica),
            f"**Qué ves:** {gf.GRIEGAS[metrica]} de la opción {tipo} (BSM) para cada nivel "
            f"de spot, de 0.4K a 1.8K, con tus σ = {sig * 100:.0f} %, r = {r * 100:.2f} % y "
            f"T = {T:.2f} años.\n\n"
            "**Cómo leerlo:** el punto es tu opción (S actual); la línea vertical, el strike. "
            "Azul siempre es call y naranja siempre es put. Sube σ o T y la curva se aplana "
            "alrededor de K; bájalos y se afila.\n\n"
            "**Unidades:** precio en unidades del subyacente; vega por 1 punto de vol; theta "
            "por día.")

    with tab_escalera:
        Sx, vencs, data = ui.escaleras_griegas(S, K, r, sig, T, tipo)
        ui.grafico_con_nota(
            gf.fig_escaleras(modo, Sx, vencs, data, S, K, tipo),
            f"**Qué ves:** las cuatro griegas del {tipo} contra el spot para varios "
            f"vencimientos: 7 días, T/4, T/2 y T. Es la 'escalera' que un operador usa para "
            "ver cómo se transformará su posición al pasar el tiempo.\n\n"
            "**Cómo leerlo:** el color más oscuro es el vencimiento más largo; las líneas "
            "verticales marcan K y tu S. Al acercarse el vencimiento, delta se vuelve un "
            "escalón en K, gamma y theta se concentran en el dinero y vega se desvanece. "
            "Lejos del dinero todo tiende a cero.\n\n"
            "**Unidades:** vega por 1 punto de vol; theta por día.")

    with tab_pares:
        ui.panel_pares_griegas(modo, S, K, r, sig, T, tipo)

    with tab_matriz:
        metrica_m = st.segmented_control("Métrica de la matriz", ["price", "delta", "gamma", "vega", "theta"],
                                         default="price", format_func=gf.GRIEGAS.get,
                                         key="g_metrica_matriz") or "price"
        Ss, sigs_pct, grid = ui.matriz_sensibilidad(metrica_m, S, K, r, sig, T, tipo)
        fig = gf.fig_mapa(modo, grid, Ss, sigs_pct, "Spot S", "Volatilidad σ (%)",
                          f"{gf.GRIEGAS[metrica_m]} del {tipo} en spot × volatilidad",
                          (S, sig * 100), gf.GRIEGAS[metrica_m], color_tipo(modo, tipo))
        ui.grafico_con_nota(
            fig,
            f"**Qué ves:** la matriz de sensibilidad clásica del libro: {gf.GRIEGAS[metrica_m]} "
            "revaluada con BSM en una malla de 11 × 11 celdas centrada en tu configuración "
            "(spot ±20 %, vol ±10 puntos).\n\n"
            "**Cómo leerlo:** eje x = spot, eje y = volatilidad en % anual; el color codifica "
            "el valor según la barra de la derecha. El punto marca tu S y σ. Recorre una fila "
            "para ver el efecto del spot con vol fija; una columna, el de la vol con spot fijo.\n\n"
            "**Unidades:** las de la métrica elegida; vol en %.")
        with st.expander("Ver como tabla"):
            st.dataframe(pd.DataFrame(grid, index=[f"σ = {x:.0f} %" for x in sigs_pct],
                                      columns=[f"S = {x:.1f}" for x in Ss]).round(4),
                         width="stretch")

    with tab_cadena:
        cadena = ui.cadena_opciones(S, K, r, sig, T)
        st.dataframe(
            cadena, hide_index=True, width="stretch",
            column_order=["Call", "Δ call", "Θ call", "Γ", "ν", "Strike", "Put", "Δ put", "Θ put"],
            column_config={
                "Call": st.column_config.NumberColumn(format="%.4f"),
                "Put": st.column_config.NumberColumn(format="%.4f"),
                "Δ call": st.column_config.NumberColumn(format="%.3f"),
                "Δ put": st.column_config.NumberColumn(format="%.3f"),
                "Θ call": st.column_config.NumberColumn("Θ call /día", format="%.4f"),
                "Θ put": st.column_config.NumberColumn("Θ put /día", format="%.4f"),
                "Γ": st.column_config.NumberColumn(format="%.5f"),
                "ν": st.column_config.NumberColumn("ν /1 pt", format="%.4f"),
                "Strike": st.column_config.NumberColumn(format="%.2f"),
            })
        ui.nota(
            f"**Qué ves:** la cadena de opciones como en un monitor de mercado: calls a la "
            f"izquierda, puts a la derecha, un strike por fila alrededor de K = {K:g}, todo "
            f"valuado con BSM a σ = {sig * 100:.0f} % plana. Gamma y vega son iguales para call "
            "y put del mismo strike, por eso van al centro.\n\n"
            "**Cómo leerlo:** la fila con strike ≈ S es la opción en el dinero: delta cerca "
            "de ±0.5, gamma y vega máximas. Hacia abajo los calls entran en el dinero y los "
            "puts salen; hacia arriba, lo contrario. En un monitor real cada fila trae además "
            "bid/ask, volumen e interés abierto, y la vol implícita cambia por strike: eso es "
            "la sonrisa, que verás en el dashboard de valuación.\n\n"
            "**Unidades:** precios en unidades del subyacente; theta por día; vega por 1 punto.")

    ui.pie("griegas")


if __name__ == "__main__":
    st.set_page_config(page_title=f"Griegas · {ui.LIBRO['titulo']}", page_icon="📐", layout="wide")
    ui.barra_lateral("griegas")
    render()
