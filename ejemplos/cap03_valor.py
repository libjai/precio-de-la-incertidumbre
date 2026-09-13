#!/usr/bin/env python3
"""Capítulo 3 — La arquitectura del precio: valor intrínseco + valor temporal.
Ejecuta: python ejemplos/cap03_valor.py

Descompone el precio Black-Scholes de una call (K = 100, σ = 25 %, r = 5 %, T = 1 año) en
lo que valdría si se ejerciera hoy (intrínseco) y lo que se paga por esperar (temporal).
El valor temporal es máximo en el dinero y se desvanece lejos de K. Guarda cap03_valor.png."""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from opciones import BlackScholes

K, r, sig, T = 100.0, 0.05, 0.25, 1.0
S = np.linspace(60, 145, 300)
intrinseco = np.maximum(S - K, 0.0)
precio = np.array([BlackScholes(s, K, r, sig, T, tipo="call").price() for s in S])
temporal = precio - intrinseco

fig, ax = plt.subplots(figsize=(8.5, 5), layout="constrained")
ax.fill_between(S, precio, intrinseco, color="#0F9E86", alpha=0.30, label="Valor temporal")
ax.plot(S, precio, color="#2B62C9", lw=2.6, label="Precio de la call (Black-Scholes)")
ax.plot(S, intrinseco, color="#C93B3B", lw=2.0, label="Valor intrínseco máx(S − K, 0)")
ax.axvline(K, color="#888", lw=0.9)
ax.annotate("K = 100", (K, 1.5), textcoords="offset points", xytext=(5, 0), color="#666")
ax.annotate("OTM", (78, 1.2), color="#666", ha="center")
ax.annotate("ITM", (125, 1.2), color="#666", ha="center")
ax.set_xlabel("Precio del subyacente, $S$")
ax.set_ylabel("Valor de la opción por acción")
ax.set_title("Precio = valor intrínseco + valor temporal (call, K = 100, σ = 25 %, r = 5 %, T = 1 año)")
ax.legend(frameon=False, loc="upper left")
ax.set_ylim(bottom=0)
ax.grid(alpha=0.3)

for s in (80, 100, 120):
    i = int(np.argmin(np.abs(S - s)))
    print(f"S = {S[i]:6.1f}  precio = {precio[i]:7.4f}  intrínseco = {intrinseco[i]:7.4f}  "
          f"temporal = {temporal[i]:7.4f}")
print(f"Valor temporal máximo: {temporal.max():.4f} en S ≈ {S[np.argmax(temporal)]:.1f} (en el dinero)")
salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cap03_valor.png")
fig.savefig(salida, dpi=150)
print(f"Figura guardada en {salida}")
