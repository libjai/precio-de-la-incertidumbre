#!/usr/bin/env python3
"""Dashboard interactivo de valuación — libro 'El Precio de la Incertidumbre' (Cap. 11).
Ejecuta:  streamlit run apps/dashboard_valuacion.py
Valúa una opción estilo MexDer con los tres motores del libro (BSM, binomial CRR y
Longstaff-Schwartz) y muestra el premio por ejercicio temprano y la sensibilidad σ×r."""
import os, sys
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes, BinomialTree, LongstaffSchwartz

st.set_page_config(page_title="Valuación · El Precio de la Incertidumbre", layout="wide")
st.title("⚖️ Valuación con tres motores")
st.caption("BSM · Binomial CRR · Longstaff-Schwartz — libro *El Precio de la Incertidumbre* (Cap. 11)")

with st.sidebar:
    st.header("Parámetros (declara tus supuestos)")
    S = st.slider("Spot S", 1.0, 200.0, 12.50, 0.5)
    K = st.slider("Strike K", 1.0, 200.0, 13.00, 0.5)
    sig = st.slider("Volatilidad σ", 0.05, 1.0, 0.28, 0.01)
    r = st.slider("Tasa r (continua)", 0.0, 0.20, 0.095, 0.005)
    T = st.slider("Vencimiento T (años)", 0.05, 3.0, 0.5, 0.05)
    tipo = st.radio("Tipo", ["put", "call"], horizontal=True)
    m = st.select_slider("Trayectorias LSM", [20_000, 60_000, 120_000], value=60_000)

euro = BlackScholes(S, K, r, sig, T, tipo=tipo).price()
amer = BinomialTree(S, K, r, sig, T, N=1200, tipo=tipo, americana=True).price()
lsm, se = LongstaffSchwartz(S, K, r, sig, T, tipo=tipo, m=m, n_steps=50).price()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Europea (BSM)", f"{euro:.4f}")
c2.metric("Americana (CRR)", f"{amer:.4f}")
c3.metric("Americana (LSM)", f"{lsm:.4f}", f"± {se:.4f}")
c4.metric("Premio ejercicio temprano", f"{amer - euro:.4f}")

st.divider()
st.subheader("Mapa de sensibilidad del precio americano (σ × r)")
sigs = np.linspace(max(0.05, sig - 0.15), sig + 0.15, 9)
rs = np.linspace(max(0.0, r - 0.04), r + 0.04, 9)
grid = np.array([[BinomialTree(S, K, rr, ss, T, N=300, tipo=tipo, americana=True).price()
                  for ss in sigs] for rr in rs])
fig, ax = plt.subplots(figsize=(8, 4.2))
im = ax.imshow(grid, aspect="auto", origin="lower", cmap="viridis",
               extent=[sigs[0], sigs[-1], rs[0], rs[-1]])
ax.scatter([sig], [r], marker="x", s=90, c="white", linewidths=2.2)
ax.set_xlabel("Volatilidad σ"); ax.set_ylabel("Tasa r")
fig.colorbar(im, ax=ax, label="Precio")
st.pyplot(fig, use_container_width=True)

st.caption("Los tres motores deben contarse la misma historia: si divergen, investiga "
           "antes de confiar. Supuestos y limitaciones: ver Cap. 11 del libro.")
