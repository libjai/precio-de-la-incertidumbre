#!/usr/bin/env python3
"""Dashboard interactivo de griegas — libro 'El Precio de la Incertidumbre' (Cap. 6).
Ejecuta:  streamlit run apps/dashboard_griegas.py   (o el hub: streamlit run apps/app.py)
Las vistas de una mesa de opciones sobre una opción europea (BSM): P&L con cono de ±1σ,
curva vs. spot, escaleras de griegas por vencimiento, pares del analista, matriz de
sensibilidad y cadena de opciones. Cifras por acción, por contrato (100 acciones, MexDer)
y por posición.
Unidades de mercado: vol y tasa en % anual; vega y rho por 1 punto porcentual; theta por día."""
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
                  "las griegas son las derivadas del precio: dicen cuánto cambia la prima y por qué. "
                  "Mueve un parámetro y observa cómo responden todas a la vez, por acción y por "
                  "contrato.")

    with st.sidebar:
        st.header("Parámetros de la opción")
        S = st.slider("Spot S (MXN por acción)", 10.0, 200.0, 100.0, 1.0, key="g_S",
                      help="Precio actual de la acción.")
        K = st.slider("Strike K (MXN)", 10.0, 200.0, 100.0, 1.0, key="g_K",
                      help="Precio de ejercicio.")
        sig = st.slider("Volatilidad σ (% anual)", 1.0, 100.0, 25.0, 1.0, key="g_sig",
                        help="Cuánto se mueve la acción en un año 'normal'. 25 = 25 %.") / 100
        r = st.slider("Tasa r (% anual, continua)", 0.0, 20.0, 5.0, 0.25, key="g_r",
                      help="Tasa libre de riesgo (referencia: TIIE / Cetes).") / 100
        T = st.slider("Tiempo al vencimiento T (años)", 0.05, 3.0, 1.0, 0.05, key="g_T",
                      help="1.0 = un año; 0.5 = seis meses (≈ 182 días); 0.25 = tres meses.")
        st.caption(f"T = {gf.etiqueta_plazo(T)} · T/2 = {gf.etiqueta_plazo(T / 2)} · "
                   f"T/4 = {gf.etiqueta_plazo(T / 4)}")
        tipo = st.radio("Tipo", ["call", "put"], horizontal=True, key="g_tipo")
        comparar = st.toggle("Mostrar la opción contraria", value=True, key="g_comparar")
    contratos = ui.parametros_posicion()
    ui.glosario()

    act = gf.griegas_actuales(S, K, r, sig, T, tipo)
    st.markdown("**Por acción (como se cotiza la prima)**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Prima (MXN por acción)", f"{act['price']:.4f}", border=True,
              help="Precio de la opción por acción, según BSM.")
    c1.metric("Delta Δ", f"{act['delta']:.4f}", border=True,
              help="Pesos que cambia la prima por cada peso que sube el spot. Se lee también "
                   "como fracción de acción equivalente.")
    c2.metric("Gamma Γ", f"{act['gamma']:.5f}", border=True,
              help="Cuánto cambia delta si el spot sube 1 peso.")
    c2.metric("Vega ν (MXN por 1 pp de vol)", f"{act['vega']:.4f}", border=True,
              help="Pesos que cambia la prima si σ sube 1 punto porcentual (de 25 % a 26 %). "
                   "No es por punto base.")
    c3.metric("Theta Θ (MXN por día)", f"{act['theta']:.4f}", border=True,
              help="Pesos que pierde la prima por cada día calendario que pasa (Θ anual / 365).")
    c3.metric("Rho ρ (MXN por 1 pp de tasa)", f"{act['rho']:.4f}", border=True,
              help="Pesos que cambia la prima si r sube 1 punto porcentual.")
    ui.nota_unidades_griegas()
    ui.fila_posicion(act, contratos)

    tab_pl, tab_curva, tab_escalera, tab_pares, tab_matriz, tab_cadena = st.tabs(
        ["P&L y valor", "Curva vs. spot", "Escaleras por vencimiento", "Pares del analista",
         "Matriz de sensibilidad", "Cadena de opciones"])

    with tab_pl:
        lect = gf.lectura_mercado(S, K, r, sig, T, tipo)
        m1, m2, m3 = st.columns(3)
        m1.metric("Prob. de terminar dentro del dinero", f"{lect['p_itm'] * 100:.1f} %", border=True,
                  help="Probabilidad riesgo-neutral N(d₂) (call) o N(−d₂) (put). No es una "
                       "probabilidad 'real': descuenta la prima de riesgo.")
        m2.metric("Movimiento esperado ±1σ al vencimiento", f"± {lect['mov_1s']:.2f} MXN", border=True,
                  help=f"S·σ·√T. Rango aproximado {lect['S_lo']:.2f} – {lect['S_hi']:.2f} "
                       "(≈ 68 % de los escenarios bajo el modelo).")
        m3.metric("Punto de equilibrio al vencimiento", f"{lect['equilibrio']:.2f} MXN", border=True,
                  help="K + prima (call) o K − prima (put), comprando al precio BSM.")
        factor, escala = ui.selector_escala(contratos, key="g_escala_pl")
        d = ui.payoff_y_valor(S, K, r, sig, T, tipo)
        ui.grafico_con_nota(
            gf.fig_payoff(modo, d, S, K, T, tipo, lect, factor, escala.lower(), ui.MONEDA),
            f"**Qué ves:** la ganancia o pérdida de un {tipo} largo comprado hoy a "
            f"{d['prima']:.4f} MXN por acción ({d['prima'] * factor:,.2f} MXN {escala.lower()}), "
            "para cada nivel del subyacente. Tres momentos: al vencimiento (línea quebrada, con "
            "zonas verde y roja), a mitad del plazo (tenue) y hoy (curva suave). Es la pantalla "
            "de escenarios de cualquier plataforma de opciones.\n\n"
            f"**Qué es T/2:** T es el tiempo que falta al vencimiento, en años. Con tu T = "
            f"{gf.etiqueta_plazo(T)}, la mitad del plazo es {gf.etiqueta_plazo(T / 2)}: la curva "
            "tenue muestra cómo valdría la opción ese día si el spot estuviera en cada nivel.\n\n"
            "**Cómo leerlo:** eje x = spot al evaluar, eje y = P&L en pesos. La banda sombreada "
            "es el rango de ±1σ del subyacente al vencimiento: lo que el mercado considera "
            "'normal'. La distancia entre la curva de hoy y la del vencimiento es el valor tiempo "
            "que theta irá consumiendo.\n\n"
            f"**Unidades:** pesos {escala.lower()}. Un contrato = {ui.LOTE} acciones (MexDer).")

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
            f"T = {gf.etiqueta_plazo(T)}.\n\n"
            "**Cómo leerlo:** el punto es tu opción (S actual); la línea vertical, el strike. "
            "Azul siempre es call y naranja siempre es put. Sube σ o T y la curva se aplana "
            "alrededor de K; bájalos y se afila.\n\n"
            f"**Unidades:** pesos por acción; multiplica por {ui.LOTE} para el contrato. Vega "
            "por 1 punto porcentual de vol; theta por día.")

    with tab_escalera:
        Sx, vencs, data = ui.escaleras_griegas(S, K, r, sig, T, tipo)
        ui.grafico_con_nota(
            gf.fig_escaleras(modo, Sx, vencs, data, S, K, tipo, T),
            f"**Qué ves:** las cuatro griegas del {tipo} contra el spot para cuatro tiempos al "
            f"vencimiento: 7 días, T/4 = {gf.etiqueta_plazo(T / 4)}, T/2 = "
            f"{gf.etiqueta_plazo(T / 2)} y T = {gf.etiqueta_plazo(T)}. Es la 'escalera' que un "
            "operador usa para anticipar cómo se transformará su posición conforme pase el tiempo.\n\n"
            "**Qué significan T/4 y T/2:** fracciones del plazo que configuraste. Si T es un "
            "año, T/4 son tres meses y T/2 seis meses. La línea de 7 días muestra la opción "
            "en su última semana.\n\n"
            "**Cómo leerlo:** el color más oscuro es el vencimiento más largo; las líneas "
            "verticales marcan K y tu S. Al acercarse el vencimiento, delta se vuelve un "
            "escalón en K, gamma y theta se concentran en el dinero y vega se desvanece. "
            "Lejos del dinero todo tiende a cero.\n\n"
            "**Unidades:** pesos por acción; vega por 1 punto porcentual; theta por día.")

    with tab_pares:
        ui.panel_pares_griegas(modo, S, K, r, sig, T, tipo)

    with tab_matriz:
        metrica_m = st.segmented_control("Métrica de la matriz", ["price", "delta", "gamma", "vega", "theta"],
                                         default="price", format_func=gf.GRIEGAS.get,
                                         key="g_metrica_matriz") or "price"
        Ss, sigs_pct, grid = ui.matriz_sensibilidad(metrica_m, S, K, r, sig, T, tipo)
        fig = gf.fig_mapa(modo, grid, Ss, sigs_pct, "Spot S (MXN)", "Volatilidad σ (%)",
                          f"{gf.GRIEGAS[metrica_m]} del {tipo} en spot × volatilidad",
                          (S, sig * 100), gf.GRIEGAS[metrica_m], color_tipo(modo, tipo))
        ui.grafico_con_nota(
            fig,
            f"**Qué ves:** la matriz de sensibilidad clásica del libro: {gf.GRIEGAS[metrica_m]} "
            "revaluada con BSM en una malla de 11 × 11 celdas centrada en tu configuración "
            "(spot ±20 %, vol ±10 puntos porcentuales).\n\n"
            "**Cómo leerlo:** eje x = spot, eje y = volatilidad en % anual; el color codifica "
            "el valor según la barra de la derecha. El punto marca tu S y σ. Recorre una fila "
            "para ver el efecto del spot con vol fija; una columna, el de la vol con spot fijo.\n\n"
            f"**Unidades:** las de la métrica elegida, por acción; vol en %. Multiplica por "
            f"{ui.LOTE} para el contrato.")
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
                "Call": st.column_config.NumberColumn("Call (MXN/acción)", format="%.4f"),
                "Put": st.column_config.NumberColumn("Put (MXN/acción)", format="%.4f"),
                "Δ call": st.column_config.NumberColumn(format="%.3f"),
                "Δ put": st.column_config.NumberColumn(format="%.3f"),
                "Θ call": st.column_config.NumberColumn("Θ call /día", format="%.4f"),
                "Θ put": st.column_config.NumberColumn("Θ put /día", format="%.4f"),
                "Γ": st.column_config.NumberColumn(format="%.5f"),
                "ν": st.column_config.NumberColumn("ν /1 pp vol", format="%.4f"),
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
            "bid/ask (precio de compra y venta), volumen e interés abierto, y la vol implícita "
            "cambia por strike: eso es la sonrisa, que verás en el dashboard de valuación.\n\n"
            f"**Unidades:** precios en pesos por acción (× {ui.LOTE} = precio del contrato); "
            "theta por día; vega por 1 punto porcentual.")

    ui.pie("griegas")


if __name__ == "__main__":
    st.set_page_config(page_title=f"Griegas · {ui.LIBRO['titulo']}", page_icon="📐", layout="wide")
    ui.barra_lateral("griegas")
    render()
