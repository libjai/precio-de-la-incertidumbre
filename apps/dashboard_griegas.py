#!/usr/bin/env python3
"""Dashboard interactivo de griegas — libro 'El Precio de la Incertidumbre' (Cap. 6).
Ejecuta:  streamlit run apps/dashboard_griegas.py
Moderniza la 'Matriz de Sensibilidad' en Excel: explora cómo cambian precio y griegas."""
import os, sys
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes

st.set_page_config(page_title="Griegas · El Precio de la Incertidumbre", layout="wide")
st.title("🧮 Explorador de opciones y griegas")
st.caption("Black-Scholes-Merton — libro *El Precio de la Incertidumbre*")

with st.sidebar:
    st.header("Parámetros")
    S = st.slider("Spot S", 10.0, 200.0, 100.0, 1.0)
    K = st.slider("Strike K", 10.0, 200.0, 100.0, 1.0)
    sig = st.slider("Volatilidad σ", 0.01, 1.0, 0.25, 0.01)
    r = st.slider("Tasa r", 0.0, 0.20, 0.05, 0.005)
    T = st.slider("Vencimiento T (años)", 0.05, 3.0, 1.0, 0.05)
    tipo = st.radio("Tipo", ["call", "put"], horizontal=True)

op = BlackScholes(S, K, r, sig, T, tipo=tipo)
c1, c2, c3 = st.columns(3)
c1.metric("Precio", f"{op.price():.4f}")
c1.metric("Delta Δ", f"{op.delta():.4f}")
c2.metric("Gamma Γ", f"{op.gamma():.5f}")
c2.metric("Vega ν (por 1%)", f"{op.vega()/100:.4f}")
c3.metric("Theta Θ (por año)", f"{op.theta():.4f}")
c3.metric("Rho ρ", f"{op.rho():.4f}")

metrica = st.selectbox("Curva a graficar vs. spot", ["price", "delta", "gamma", "vega", "theta"])
Sx = np.linspace(max(1, K*0.4), K*1.8, 200)
y = [getattr(BlackScholes(s, K, r, sig, T, tipo=tipo), metrica)() for s in Sx]
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(Sx, y, color="#0E3A5D", lw=2.4)
ax.axvline(K, color="#5C6B73", ls=":")
ax.axhline(0, color="#5C6B73", lw=0.7)
ax.set_xlabel("Spot S"); ax.set_ylabel(metrica); ax.grid(alpha=0.3)
st.pyplot(fig)
st.info("Mueve los deslizadores y observa en vivo cómo responden precio y griegas. "
        "Es la versión moderna e interactiva de las tablas de sensibilidad clásicas.")
