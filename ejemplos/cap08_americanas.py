#!/usr/bin/env python3
"""Capítulo 8 — Opciones americanas y el ejercicio óptimo.
Ejecuta: python ejemplos/cap08_americanas.py

Muestra (1) el premio por ejercicio temprano (americana vs europea) y (2) la frontera
de ejercicio óptimo extraída del árbol binomial: debajo de ella conviene EJERCER."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes, BinomialTree

S0, K, r, sig, T = 100.0, 100.0, 0.05, 0.30, 1.0

euro = BlackScholes(S0, K, r, sig, T, tipo="put").price()
amer = BinomialTree(S0, K, r, sig, T, N=1500, tipo="put", americana=True).price()
print(f"Put europea (BSM):      {euro:.4f}")
print(f"Put americana (CRR):    {amer:.4f}")
print(f"Premio por ejercicio temprano: {amer - euro:.4f}")

# Frontera de ejercicio: mayor S en el que aún conviene ejercer, en fechas selectas
N = 220
L = BinomialTree(S0, K, r, sig, T, N=N, tipo="put", americana=True).lattice()
S, E = L["S"], L["E"]
print("\nFrontera de ejercicio óptimo (S* por debajo del cual se ejerce):")
for frac in (0.25, 0.50, 0.75, 0.95):
    i = int(frac * N)
    xs = [S[i][j] for j in range(i + 1) if E[i][j]]
    if xs:
        print(f"  t = {frac * T:.2f} años  ->  S* ≈ {max(xs):.2f}")
print("\nLección: la frontera sube al acercarse el vencimiento — esperar pierde valor.")
