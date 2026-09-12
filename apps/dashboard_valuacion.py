#!/usr/bin/env python3
"""Dashboard interactivo de valuación — libro 'El Precio de la Incertidumbre' (Cap. 11).
Ejecuta:  streamlit run apps/dashboard_valuacion.py   (o el hub: streamlit run apps/app.py)
Valúa una opción estilo MexDer con los tres motores del libro (BSM, binomial CRR y
Longstaff-Schwartz): mapas de precio y premio por ejercicio temprano en S × T, frontera de
ejercicio óptimo, convergencia de los motores, precio en σ × r con el motor elegido y
vol implícita con sonrisa a partir de cotizaciones.
Unidades de mercado: vol y tasa en % anual."""
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import componentes as ui
import graficos as gf
from opciones import BlackScholes, BinomialTree, LongstaffSchwartz
from tema import color_tipo


def _tabla(grid, filas, columnas, fmt_f, fmt_c):
    with st.expander("Ver como tabla"):
        st.dataframe(pd.DataFrame(grid, index=[fmt_f.format(x) for x in filas],
                                  columns=[fmt_c.format(x) for x in columnas]).round(4),
                     width="stretch")


def render() -> None:
    modo = ui.modo_actual()
    ui.encabezado("valuacion",
                  "tres motores distintos deben contar la misma historia. Si BSM, el árbol "
                  "binomial y Longstaff-Schwartz divergen, el problema está en los supuestos, "
                  "no en el mercado.")

    with st.sidebar:
        st.header("Parámetros (declara tus supuestos)")
        S = st.slider("Spot S", 1.0, 200.0, 12.50, 0.5, key="v_S")
        K = st.slider("Strike K", 1.0, 200.0, 13.00, 0.5, key="v_K")
        sig = st.slider("Volatilidad σ (% anual)", 5.0, 100.0, 28.0, 1.0, key="v_sig") / 100
        r = st.slider("Tasa r (% anual, continua)", 0.0, 20.0, 9.5, 0.25, key="v_r") / 100
        T = st.slider("Vencimiento T (años)", 0.05, 3.0, 0.5, 0.05, key="v_T")
        tipo = st.radio("Tipo", ["put", "call"], horizontal=True, key="v_tipo")
        m = st.select_slider("Trayectorias LSM", [20_000, 60_000, 120_000], value=60_000, key="v_m")

    euro = BlackScholes(S, K, r, sig, T, tipo=tipo).price()
    amer = BinomialTree(S, K, r, sig, T, N=1200, tipo=tipo, americana=True).price()
    lsm, se = LongstaffSchwartz(S, K, r, sig, T, tipo=tipo, m=m, n_steps=50).price()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Europea (BSM)", f"{euro:.4f}", border=True)
    c2.metric("Americana (CRR, N = 1200)", f"{amer:.4f}", border=True)
    c3.metric("Americana (LSM)", f"{lsm:.4f}", f"± {se:.4f} error estándar",
              delta_color="off", border=True)
    c4.metric("Premio por ejercicio temprano", f"{amer - euro:.4f}",
              help="Americana (CRR) − Europea (BSM)", border=True)

    color = color_tipo(modo, tipo)
    tab_st, tab_frontera, tab_conv, tab_sr, tab_iv, tab_pares = st.tabs(
        ["Mapas en S × T", "Frontera de ejercicio", "Convergencia", "Precio en σ × r (elige motor)",
         "Vol implícita y sonrisa", "Pares del analista"])

    with tab_st:
        vista = st.segmented_control("Vista", ["precio", "premio"], default="precio",
                                     format_func={"precio": "Precio americano",
                                                  "premio": "Premio por ejercicio temprano"}.get,
                                     key="v_vista_st") or "precio"
        Ss, Ts, amer_g, euro_g = ui.mapa_americano(S, K, r, sig, T, tipo)
        if vista == "precio":
            fig = gf.fig_mapa(modo, amer_g, Ss, Ts, "Spot S", "Vencimiento T (años)",
                              f"Precio del {tipo} americano (binomial CRR, N = 200)", (S, T),
                              "Precio", color)
            ui.grafico_con_nota(
                fig,
                f"**Qué ves:** el precio del {tipo} americano en una malla de 9 × 9 "
                f"combinaciones de spot (±30 %) y vencimiento (0.25T a 1.75T), con σ = "
                f"{sig * 100:.0f} % y r = {r * 100:.2f} % fijos.\n\n"
                "**Cómo leerlo:** eje x = spot, eje y = años al vencimiento; el color codifica el "
                "precio según la barra de la derecha. El punto es tu configuración. Son los dos "
                "ejes que un operador mira primero: dónde está el subyacente y cuánto tiempo "
                "queda.\n\n"
                "**Unidades:** precio en unidades del subyacente; T en años.")
            _tabla(amer_g, Ts, Ss, "T = {:.2f}", "S = {:.2f}")
        else:
            fig = gf.fig_mapa(modo, amer_g - euro_g, Ss, Ts, "Spot S", "Vencimiento T (años)",
                              f"Premio por ejercicio temprano del {tipo} (americana − europea)",
                              (S, T), "Premio", color)
            ui.grafico_con_nota(
                fig,
                "**Qué ves:** cuánto vale el derecho a ejercer antes: precio americano (CRR) "
                "menos europeo (BSM) en la misma malla S × T.\n\n"
                "**Cómo leerlo:** el premio crece con la tasa, el plazo y qué tan dentro del "
                "dinero está el put. Para un call sin dividendos es prácticamente cero: nunca "
                "conviene ejercer antes (Cap. 8). Es el número que Longstaff-Schwartz debe "
                "reproducir por simulación (Cap. 9).\n\n"
                "**Unidades:** precio en unidades del subyacente.")
            _tabla(amer_g - euro_g, Ts, Ss, "T = {:.2f}", "S = {:.2f}")

    with tab_frontera:
        res = ui.frontera_ejercicio(S, K, r, sig, T, tipo)
        if res is None:
            st.info("Un call sin dividendos nunca se ejerce antes del vencimiento: su frontera "
                    "de ejercicio es infinita (Cap. 8). Cambia a **put** para ver la frontera.")
        else:
            t, frontera = res
            ui.grafico_con_nota(
                gf.fig_frontera(modo, t, frontera, S, K, T, tipo),
                "**Qué ves:** la frontera de ejercicio óptimo S*(t) del put americano, extraída "
                "del árbol CRR (N = 400): en cada fecha, el spot más alto en el que conviene "
                "ejercer en vez de esperar.\n\n"
                "**Cómo leerlo:** eje x = tiempo transcurrido, eje y = spot. Por debajo de la "
                "curva (zona sombreada) se ejerce; por encima se espera. La frontera sube hacia "
                "K al acercarse el vencimiento: cuanto menos tiempo queda, menos vale esperar. "
                "Es exactamente la regla de parada que Longstaff-Schwartz aprende por regresión "
                "(Cap. 9). Tu spot de hoy está marcado en t = 0.\n\n"
                "**Unidades:** spot en unidades del subyacente; tiempo en años.")

    with tab_conv:
        Ns, crr_a, crr_e, bsm = ui.convergencia_crr(S, K, r, sig, T, tipo)
        ms, lsm_p, lsm_se, ref = ui.convergencia_lsm(S, K, r, sig, T, tipo)
        st.pyplot(gf.fig_convergencia(modo, Ns, crr_a, crr_e, bsm, ms, lsm_p, lsm_se, ref, tipo),
                  width="stretch")
        ui.nota(
            "**Qué ves:** la prueba de que los tres motores cuentan la misma historia. "
            "Izquierda: el precio binomial al aumentar los pasos N; la europea CRR debe "
            "converger a BSM (línea gris) y la americana, a su propio límite, por encima. "
            "Derecha: el precio de Longstaff-Schwartz al aumentar las trayectorias, con su "
            "banda de ±1.96 errores estándar; la línea gris es la americana CRR con N = 1200.\n\n"
            "**Cómo leerlo:** ambos ejes x son logarítmicos. El zigzag par-impar del binomial es "
            "normal (Cap. 4). La banda de LSM se estrecha con √m: cuadruplicar las trayectorias "
            "reduce el error a la mitad (Cap. 7). Si la línea gris cae fuera de la banda con "
            "muchas trayectorias, sospecha del número de pasos o de las funciones base (Cap. 9).\n\n"
            "**Unidades:** precio en unidades del subyacente.")

    with tab_sr:
        motor = st.selectbox("Motor de valuación", list(gf.MOTORES), format_func=gf.MOTORES.get,
                             key="v_motor")
        sigs_pct, rs_pct, grid = ui.mapa_sigma_r(S, K, r, sig, T, tipo, motor)
        fig = gf.fig_mapa(modo, grid, sigs_pct, rs_pct, "Volatilidad σ (%)", "Tasa r (%)",
                          f"Precio del {tipo} en volatilidad × tasa · {gf.MOTORES[motor]}",
                          (sig * 100, r * 100), "Precio", color)
        nota_lsm = ("\n\n**Ojo:** LSM es Monte Carlo: cada celda trae ruido estadístico "
                    "(10 000 trayectorias); si el mapa se ve granulado, es el error de "
                    "simulación, no el mercado (Cap. 9)." if motor == "LSM" else "")
        ui.grafico_con_nota(
            fig,
            f"**Qué ves:** el precio del {tipo} con el motor elegido, en una malla de vol "
            "(±15 puntos) y tasa (±4 puntos) alrededor de tu configuración, con S, K y T fijos.\n\n"
            "**Cómo leerlo:** eje x = volatilidad, eje y = tasa, ambas en % anual; el color "
            "codifica el precio según la barra de la derecha. Recorre una fila para ver la vega "
            "(efecto de σ con r fija) y una columna para ver la rho (efecto de r con σ fija). "
            "Cambia el motor: BSM valúa la europea; CRR y LSM la americana, y la diferencia "
            "entre ellos es el premio por ejercicio temprano." + nota_lsm)
        _tabla(grid, rs_pct, sigs_pct, "r = {:.2f} %", "σ = {:.0f} %")

    with tab_iv:
        col_son, col_map = st.columns(2)
        with col_son:
            st.markdown("**Sonrisa a partir de cotizaciones** (edita la tabla con precios reales)")
            if "v_cotiz_base" not in st.session_state or st.session_state.get("v_cotiz_params") != (S, K, r, sig, T, tipo):
                st.session_state["v_cotiz_base"] = gf.cotizaciones_ejemplo(S, K, r, sig, T, tipo)
                st.session_state["v_cotiz_params"] = (S, K, r, sig, T, tipo)
            cotiz = st.data_editor(st.session_state["v_cotiz_base"], num_rows="dynamic", hide_index=True,
                                   width="stretch", key="v_cotiz_editor",
                                   column_config={"Strike": st.column_config.NumberColumn(format="%.2f"),
                                                  "Precio de mercado": st.column_config.NumberColumn(format="%.4f")})
            cotiz = cotiz.dropna()
            df_son = gf.sonrisa(S, r, T, tipo, cotiz) if len(cotiz) else None
            if df_son is not None and df_son["Vol implícita (%)"].notna().any():
                st.pyplot(gf.fig_sonrisa(modo, df_son, sig, K, tipo), width="stretch")
            else:
                st.warning("Ninguna cotización tiene vol implícita válida: revisa que los precios "
                           "respeten las cotas de no arbitraje (Cap. 10).")
            ui.nota(
                f"**Qué ves:** la vol implícita que BSM necesita para reproducir cada precio "
                f"observado del {tipo}, por strike, con S = {S:g}, r = {r * 100:.2f} % y T = {T:.2f} "
                "fijos. La línea gris es la σ plana de tu modelo. Las cotizaciones iniciales son "
                "sintéticas con skew de renta variable (más vol en strikes bajos): sustitúyelas "
                "por precios de mercado y verás la sonrisa real.\n\n"
                "**Cómo leerlo:** si la curva no es plana, el mercado no cree en BSM con una sola "
                "σ: paga más protección abajo (skew) o en las colas (sonrisa). Un punto que "
                "desaparece es un precio que viola las cotas de no arbitraje (Cap. 10). Es la "
                "pantalla de superficie de vol de cualquier terminal, reducida a un vencimiento.\n\n"
                "**Unidades:** vol en % anual; precios en unidades del subyacente.")
        with col_map:
            st.markdown("**Vol implícita en strike × precio** (la inversión completa)")
            Ks, Ps_iv, iv_g = ui.mapa_vol_implicita(S, K, r, T, tipo)
            fig = gf.fig_mapa(modo, iv_g, Ks, Ps_iv, "Strike K", f"Precio del {tipo}",
                              f"Vol implícita del {tipo} (%) en strike × precio",
                              (K, euro), "Vol implícita (%)", color, "tu opción (precio BSM)")
            st.pyplot(fig, width="stretch")
            ui.nota(
                "**Qué ves:** la misma inversión precio → vol, pero para toda la malla de strikes "
                "(0.85K a 1.15K) y precios: cada celda responde '¿qué vol justifica pagar este "
                "precio por este strike?'.\n\n"
                "**Cómo leerlo:** eje x = strike, eje y = precio; el color es la vol implícita en "
                "% anual según la barra. Subir por una columna es pagar más por la misma opción, "
                "es decir, más vol implícita. Las celdas vacías son precios imposibles para ese "
                "strike (cotas de no arbitraje). El punto es tu opción al precio BSM.\n\n"
                f"**Rango de precios:** el que producen vols de 8 % a 70 % en K = {K:g}.")
            _tabla(iv_g, Ps_iv, Ks, "P = {:.3f}", "K = {:.2f}")
        with st.expander("Vista no estándar: tasa implícita en strike × precio (σ fija)"):
            Ks2, Ps_ir, ir_g = ui.mapa_tasa_implicita(S, K, sig, T, tipo)
            fig = gf.fig_mapa(modo, ir_g, Ks2, Ps_ir, "Strike K", f"Precio del {tipo}",
                              f"Tasa implícita del {tipo} (%) en strike × precio",
                              (K, euro), "Tasa implícita (%)", color, "tu opción (precio BSM)")
            ui.grafico_con_nota(
                fig,
                f"**Qué ves:** la tasa continua que BSM necesita para reproducir cada precio del "
                f"{tipo} con σ = {sig * 100:.0f} % fija. Es el espejo de la vol implícita: aquí se "
                "despeja r. No es una pantalla habitual de mesa; en la práctica la tasa implícita "
                "se lee por paridad put-call con call y put del mismo strike.\n\n"
                "**Cómo leerlo:** mismos ejes; el color es la tasa en % anual. En un call, más "
                "precio exige más tasa; en un put, menos. Como rho es pequeña frente a vega, el "
                "mismo cambio de precio requiere mover mucho más la tasa que la vol: por eso el "
                "rango es tan amplio. Celdas vacías: sin solución entre −10 % y 60 %.")
            _tabla(ir_g, Ps_ir, Ks2, "P = {:.3f}", "K = {:.2f}")

    with tab_pares:
        ui.panel_pares_griegas(modo, S, K, r, sig, T, tipo)

    ui.pie("valuacion")


if __name__ == "__main__":
    st.set_page_config(page_title=f"Valuación · {ui.LIBRO['titulo']}", page_icon="⚖️", layout="wide")
    ui.barra_lateral("valuacion")
    render()
