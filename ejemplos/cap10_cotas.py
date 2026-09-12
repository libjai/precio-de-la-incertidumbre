#!/usr/bin/env python3
"""Capítulo 10 — Robustez: ¿qué tan confiable es mi precio LSM?
Ejecuta: python ejemplos/cap10_cotas.py

Tres diagnósticos del capítulo, en vivo:
  1) LSM contra una referencia determinista (árbol binomial fino): el sesgo bajo.
  2) Sensibilidad a las funciones base (grado del polinomio).
  3) Dispersión entre semillas: el error de Monte Carlo no es decorativo.
Nota (libro, §10.1): la cota inferior es rigurosa solo out-of-sample (two-pass);
aquí LSM se evalúa in-sample, por lo que puede asomar sesgo de previsión."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BinomialTree, LongstaffSchwartz

S0, K, r, sig, T = 36.0, 40.0, 0.06, 0.20, 1.0

ref = BinomialTree(S0, K, r, sig, T, N=4000, tipo="put", americana=True).price()
print(f"Referencia (binomial N=4000): {ref:.4f}\n")

print("1) LSM vs referencia (deg=3, m=100k):")
p, se = LongstaffSchwartz(S0, K, r, sig, T, tipo="put", m=100_000, n_steps=50).price()
print(f"   LSM: {p:.4f} ± {se:.4f}   (diferencia vs ref: {p - ref:+.4f})\n")

print("2) Sensibilidad a las funciones base (grado del polinomio):")
for deg in (2, 3, 5):
    p, se = LongstaffSchwartz(S0, K, r, sig, T, tipo="put",
                              m=100_000, n_steps=50, deg=deg).price()
    print(f"   deg={deg}:  {p:.4f} ± {se:.4f}")
print()

print("3) Dispersión entre semillas (misma configuración, distinto azar):")
for seed in (7, 42, 2024):
    p, se = LongstaffSchwartz(S0, K, r, sig, T, tipo="put",
                              m=100_000, n_steps=50, seed=seed).price()
    print(f"   seed={seed:4d}:  {p:.4f} ± {se:.4f}")

print("\nLección: reporta el precio con su intervalo y una referencia independiente;")
print("un número solo, sin cota ni error, no es un resultado profesional.")
