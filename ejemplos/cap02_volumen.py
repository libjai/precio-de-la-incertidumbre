#!/usr/bin/env python3
"""Capítulo 2 — La brecha de liquidez del MexDer: futuros frente a opciones.
Ejecuta: python ejemplos/cap02_volumen.py

Contratos negociados en un mes (marzo de 2026, cifras aproximadas del boletín del MexDer)
en escala logarítmica: los futuros mueven unas 95 veces más contratos que las opciones.
Sustituye `vals` por los datos del mes que te interese. Guarda cap02_volumen.png."""
import os

import matplotlib.pyplot as plt

cats = ["Futuros", "Opciones"]
vals = [2_200_000, 23_100]

fig, ax = plt.subplots(figsize=(8, 4.6), layout="constrained")
barras = ax.bar(cats, vals, color=["#2B62C9", "#E0702E"], width=0.5, zorder=3)
ax.set_yscale("log")
ax.set_ylim(1e3, 2e7)
ax.set_ylabel("Contratos negociados (escala log)")
ax.grid(axis="y", which="major", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
for b, v in zip(barras, vals):
    ax.annotate(f"{v:,.0f}", (b.get_x() + b.get_width() / 2, v), textcoords="offset points",
                xytext=(0, 7), ha="center", fontsize=12, weight="bold")
razon = vals[0] / vals[1]
ax.text(0.5, 5e6, f"≈ {razon:.0f}× más futuros\nque opciones", ha="center", va="center",
        fontsize=12, color="#C93B3B", weight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#C93B3B", lw=1.2))
ax.set_title("La brecha de liquidez del MexDer: futuros vs. opciones (marzo 2026, aprox.)")

print(f"Futuros: {vals[0]:,} contratos · Opciones: {vals[1]:,} contratos · razón ≈ {razon:.0f}×")
salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cap02_volumen.png")
fig.savefig(salida, dpi=150)
print(f"Figura guardada en {salida}")
