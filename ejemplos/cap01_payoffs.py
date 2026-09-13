#!/usr/bin/env python3
"""Capítulo 1 — Las cuatro posiciones básicas en opciones: diagramas de ganancia/pérdida.
Ejecuta: python ejemplos/cap01_payoffs.py

Call larga, put larga, call corta y put corta al vencimiento, con prima = 8 y K = 100.
La asimetría es la idea central del capítulo: quien compra paga la prima y limita su
pérdida; quien vende la cobra y asume la obligación. Guarda cap01_payoffs.png junto al script."""
import os

import matplotlib.pyplot as plt
import numpy as np

K, prima = 100.0, 8.0
S = np.linspace(60, 140, 400)


def ganancia(tipo, posicion):
    intrinseco = np.maximum(S - K, 0) if tipo == "call" else np.maximum(K - S, 0)
    return intrinseco - prima if posicion == "larga" else prima - intrinseco


casos = [("call", "larga", "Call larga (derecho a comprar)"),
         ("put", "larga", "Put larga (derecho a vender)"),
         ("call", "corta", "Call corta (obligación de vender)"),
         ("put", "corta", "Put corta (obligación de comprar)")]

fig, axes = plt.subplots(2, 2, figsize=(10, 7), layout="constrained")
for ax, (tipo, pos, titulo) in zip(axes.ravel(), casos):
    g = ganancia(tipo, pos)
    ax.axhline(0, color="#888", lw=1)
    ax.axvline(K, color="#888", lw=0.8)
    ax.fill_between(S, g, 0, where=g >= 0, color="#1B8F4E", alpha=0.18)
    ax.fill_between(S, g, 0, where=g < 0, color="#C93B3B", alpha=0.18)
    ax.plot(S, g, color="#2B62C9", lw=2.4)
    ax.set_title(titulo, fontsize=11)
    ax.set_xlabel("Precio del subyacente al vencimiento, $S_T$")
    ax.set_ylabel("Ganancia / pérdida por acción")
    ax.grid(alpha=0.3)
    print(f"{titulo:36s} pérdida máx = {g.min():7.2f}   ganancia máx = "
          f"{'ilimitada' if g.max() > 30 else f'{g.max():.2f}'}")

fig.suptitle("Las cuatro posiciones básicas (prima = 8, K = 100)", fontsize=13)
salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cap01_payoffs.png")
fig.savefig(salida, dpi=150)
print(f"\nFigura guardada en {salida}")
