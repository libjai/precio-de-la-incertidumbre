#!/usr/bin/env python3
"""Capítulo 5 — Black-Scholes-Merton. Ejemplos reproducibles.
Ejecuta:  python ejemplos/cap05_black_scholes.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes

op = BlackScholes(S=100, K=100, r=0.05, sigma=0.20, T=1, tipo="call")
print(f"Call BSM: {op.price():.4f}")
put = BlackScholes(S=100, K=100, r=0.05, sigma=0.20, T=1, tipo="put")
print(f"Put  BSM: {put.price():.4f}  (paridad: C-P = S - K e^-rT)")
print(f"Delta={op.delta():.4f}  Gamma={op.gamma():.4f}  Vega(1.0)={op.vega():.4f}")
print(f"Theta={op.theta():.4f}  Rho={op.rho():.4f}")

# Efecto de la volatilidad
for s in (0.10, 0.20, 0.40):
    print(f"sigma={s:.0%} -> call = {BlackScholes(100,100,0.05,s,1,tipo='call').price():.4f}")
