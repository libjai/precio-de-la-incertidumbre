#!/usr/bin/env python3
"""Capítulo 9 — Longstaff-Schwartz. Ejecuta: python ejemplos/cap09_longstaff_schwartz.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import LongstaffSchwartz, BinomialTree
binom = BinomialTree(36, 40, 0.06, 0.20, 1, N=2000, tipo="put", americana=True).price()
lsm, err = LongstaffSchwartz(36, 40, 0.06, 0.20, 1, tipo="put", m=100_000, n_steps=50).price()
print(f"Put americana 36/40 — Binomial: {binom:.4f} | LSM: {lsm:.4f} ± {err:.4f}")
