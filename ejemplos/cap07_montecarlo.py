#!/usr/bin/env python3
"""Capítulo 7 — Monte Carlo. Ejecuta: python ejemplos/cap07_montecarlo.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes, MonteCarlo
bsm = BlackScholes(100, 100, 0.05, 0.20, 1, tipo="call").price()
for m in (10_000, 100_000, 1_000_000):
    pr, err = MonteCarlo(100, 100, 0.05, 0.20, 1, tipo="call", m=m).price()
    print(f"m={m:>9,}: MC={pr:.4f} ± {err:.4f}   (BSM={bsm:.4f})")
