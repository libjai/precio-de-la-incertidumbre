#!/usr/bin/env python3
"""Capítulo 12 — Exóticas. Ejecuta: python ejemplos/cap12_exoticas.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes, precio_asiatica, precio_barrera
van = BlackScholes(100, 100, 0.05, 0.30, 1, tipo="call").price()
asi, _ = precio_asiatica(100, 100, 0.05, 0.30, 1, tipo="call")
bar, _ = precio_barrera(100, 100, 0.05, 0.30, 1, barrera=130, tipo="call", tipo_barrera="up-and-out")
print(f"Vanilla call: {van:.4f} | Asiática: {asi:.4f} | Barrera up-and-out(130): {bar:.4f}")
