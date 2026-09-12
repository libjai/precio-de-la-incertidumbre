#!/usr/bin/env python3
"""Capítulo 6 — Griegas. Ejecuta: python ejemplos/cap06_griegas.py
Dashboard interactivo: streamlit run apps/dashboard_griegas.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes
op = BlackScholes(S=100, K=100, r=0.05, sigma=0.25, T=1, tipo="call")
print(f"Precio={op.price():.4f}")
print(f"Delta={op.delta():.4f}  Gamma={op.gamma():.5f}  Vega={op.vega():.4f}  Theta={op.theta():.4f}  Rho={op.rho():.4f}")
print("Vol implícita de un precio 12.0:", round(BlackScholes(100,100,0.05,0.3,1,tipo="call").implied_vol(12.0),4))
