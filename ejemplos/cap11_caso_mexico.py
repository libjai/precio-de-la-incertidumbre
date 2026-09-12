#!/usr/bin/env python3
"""Capítulo 11 — Caso mexicano (ilustrativo). Ejecuta: python ejemplos/cap11_caso_mexico.py
Sustituye los parámetros con datos vigentes del MexDer/Cetes."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes, BinomialTree, LongstaffSchwartz
S0, K, sig, r, T = 12.50, 13.00, 0.28, 0.095, 0.5
euro = BlackScholes(S0, K, r, sig, T, tipo="put").price()
bino = BinomialTree(S0, K, r, sig, T, N=1500, tipo="put", americana=True).price()
lsm, err = LongstaffSchwartz(S0, K, r, sig, T, tipo="put", m=200_000, n_steps=60).price()
print(f"Put europea (BSM):        {euro:.4f}")
print(f"Put americana (binomial): {bino:.4f}")
print(f"Put americana (LSM):      {lsm:.4f} ± {err:.4f}")
print(f"Premio de ejercicio anticipado: {bino-euro:.4f}")
