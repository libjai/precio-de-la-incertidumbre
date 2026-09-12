#!/usr/bin/env python3
"""Capítulo 13 — Opciones reales: el premio de flexibilidad (opción de abandono).
La opción de abandonar un proyecto por un valor de rescate es una put americana sobre
el valor del proyecto. Ejecuta: python ejemplos/cap13_opciones_reales.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opciones import LongstaffSchwartz, BinomialTree

# Proyecto: valor hoy 100, rescate 90, sigma 30%, r 8%, 3 años
flex, se = LongstaffSchwartz(100, 90, 0.08, 0.30, 3, tipo="put", m=200_000, n_steps=72).price()
bench = BinomialTree(100, 90, 0.08, 0.30, 3, N=2000, tipo="put", americana=True).price()
print(f"Premio de flexibilidad (LSM): {flex:.4f} ± {se:.4f}")
print(f"Benchmark binomial:           {bench:.4f}")
print(f"Valor rígido (VPN): 100.00 | Valor con flexibilidad: {100+flex:.2f}")
