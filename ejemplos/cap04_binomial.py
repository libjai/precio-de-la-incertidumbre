#!/usr/bin/env python3
"""Capítulo 4 — Modelo binomial (CRR). Ejemplos reproducibles del libro
'El Precio de la Incertidumbre'. Ejecuta:  python ejemplos/cap04_binomial.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import BlackScholes, BinomialTree

S, K, r, sig, T = 100, 100, 0.05, 0.20, 1.0

bsm = BlackScholes(S, K, r, sig, T, tipo="call").price()
binom = BinomialTree(S, K, r, sig, T, N=2000, tipo="call").price()
print(f"Call europea  -> Black-Scholes: {bsm:.4f} | Binomial(N=2000): {binom:.4f}")

put_eu = BlackScholes(S, K, r, sig, T, tipo="put").price()
put_am = BinomialTree(S, K, r, sig, T, N=1000, tipo="put", americana=True).price()
print(f"Put europea: {put_eu:.4f} | Put americana: {put_am:.4f} | prima de ejercicio anticipado: {put_am-put_eu:.4f}")
