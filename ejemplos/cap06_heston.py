#!/usr/bin/env python3
"""Capítulo 6 — El modelo de Heston: volatilidad estocástica y sonrisa.
Ejecuta: python ejemplos/cap06_heston.py

Simula Heston con el esquema de Euler con truncamiento completo, valúa calls europeas
por Monte Carlo y muestra que la volatilidad implícita resultante NO es plana: el
modelo genera el sesgo/sonrisa que el mercado cotiza (Cap. 6 del libro).
Referencias: Heston (1993); Andersen (2008); Gatheral (2006)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes

# Parámetros (declara tus supuestos)
S0, r, T = 100.0, 0.05, 0.5
v0, kappa, theta, xi, rho = 0.04, 2.0, 0.04, 0.6, -0.7   # v0 = sigma0^2 = 20%^2
m, n_steps, seed = 100_000, 125, 42
print(f"Feller 2κθ ≥ ξ²: {'sí' if 2*kappa*theta >= xi**2 else 'no (v puede tocar 0; el esquema la trunca)'}\n")

rng = np.random.default_rng(seed)
dt = T / n_steps
S = np.full(m, S0)
v = np.full(m, v0)
for _ in range(n_steps):
    z1 = rng.standard_normal(m)
    z2 = rho * z1 + np.sqrt(1 - rho**2) * rng.standard_normal(m)
    v_pos = np.maximum(v, 0.0)                    # truncamiento completo
    S *= np.exp((r - 0.5 * v_pos) * dt + np.sqrt(v_pos * dt) * z1)
    v += kappa * (theta - v_pos) * dt + xi * np.sqrt(v_pos * dt) * z2

disc = np.exp(-r * T)
print("  K      call Heston        vol implícita")
for K in (80, 90, 100, 110, 120):
    pago = np.maximum(S - K, 0.0)
    c, se = disc * pago.mean(), disc * pago.std(ddof=1) / np.sqrt(m)
    iv = BlackScholes(S0, K, r, 0.5, T, tipo="call").implied_vol(c)
    print(f"{K:5.0f}   {c:8.4f} ± {se:.4f}     {iv:6.2%}")

print("\nLección: con vol estocástica y correlación negativa (ρ<0), los strikes bajos")
print("implican más volatilidad que los altos — el sesgo de las acciones. BSM con σ")
print("constante no puede producir esta curva; Heston se calibra para reproducirla.")
