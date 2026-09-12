#!/usr/bin/env python3
"""Módulo base de valuación de opciones — libro 'El Precio de la Incertidumbre'.

Clases reutilizables, sin dependencias más allá de la librería estándar + numpy
(numpy solo se usa en BinomialTree por comodidad; BlackScholes es stdlib pura).

    from opciones import BlackScholes, BinomialTree

Convenciones: S spot, K strike, r tasa libre de riesgo (continua), q dividendos,
sigma volatilidad, T vencimiento en años. tipo in {'call','put'}.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

SQRT2 = math.sqrt(2.0)
SQRT2PI = math.sqrt(2.0 * math.pi)


def norm_cdf(x: float) -> float:
    """CDF normal estándar (sin scipy), vía función error."""
    return 0.5 * (1.0 + math.erf(x / SQRT2))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT2PI


@dataclass
class BlackScholes:
    """Modelo Black-Scholes-Merton con dividendo continuo q."""
    S: float
    K: float
    r: float
    sigma: float
    T: float
    q: float = 0.0
    tipo: str = "call"

    def _d1_d2(self):
        if self.T <= 0 or self.sigma <= 0:
            raise ValueError("T y sigma deben ser positivos")
        d1 = (math.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T) / (
            self.sigma * math.sqrt(self.T))
        d2 = d1 - self.sigma * math.sqrt(self.T)
        return d1, d2

    def price(self) -> float:
        d1, d2 = self._d1_d2()
        disc_q = math.exp(-self.q * self.T)
        disc_r = math.exp(-self.r * self.T)
        if self.tipo == "call":
            return self.S * disc_q * norm_cdf(d1) - self.K * disc_r * norm_cdf(d2)
        return self.K * disc_r * norm_cdf(-d2) - self.S * disc_q * norm_cdf(-d1)

    # --- Griegas ---
    def delta(self) -> float:
        d1, _ = self._d1_d2()
        dq = math.exp(-self.q * self.T)
        return dq * (norm_cdf(d1) if self.tipo == "call" else norm_cdf(d1) - 1.0)

    def gamma(self) -> float:
        d1, _ = self._d1_d2()
        return math.exp(-self.q * self.T) * norm_pdf(d1) / (self.S * self.sigma * math.sqrt(self.T))

    def vega(self) -> float:
        """Por punto de vol (1.0 = 100%). Dividir entre 100 para 'por 1%'."""
        d1, _ = self._d1_d2()
        return self.S * math.exp(-self.q * self.T) * norm_pdf(d1) * math.sqrt(self.T)

    def theta(self) -> float:
        d1, d2 = self._d1_d2()
        dq, dr = math.exp(-self.q * self.T), math.exp(-self.r * self.T)
        term1 = -self.S * dq * norm_pdf(d1) * self.sigma / (2 * math.sqrt(self.T))
        if self.tipo == "call":
            return term1 - self.r * self.K * dr * norm_cdf(d2) + self.q * self.S * dq * norm_cdf(d1)
        return term1 + self.r * self.K * dr * norm_cdf(-d2) - self.q * self.S * dq * norm_cdf(-d1)

    def rho(self) -> float:
        _, d2 = self._d1_d2()
        dr = math.exp(-self.r * self.T)
        if self.tipo == "call":
            return self.K * self.T * dr * norm_cdf(d2)
        return -self.K * self.T * dr * norm_cdf(-d2)

    def implied_vol(self, precio_mercado: float, tol: float = 1e-8, itmax: int = 200) -> float:
        """Volatilidad implícita por bisección (robusta, sin scipy)."""
        lo, hi = 1e-6, 5.0
        for _ in range(itmax):
            mid = 0.5 * (lo + hi)
            self.sigma = mid
            diff = self.price() - precio_mercado
            if abs(diff) < tol:
                return mid
            # precio es creciente en sigma
            if diff > 0:
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)


@dataclass
class BinomialTree:
    """Árbol binomial de Cox-Ross-Rubinstein. Europea o americana."""
    S: float
    K: float
    r: float
    sigma: float
    T: float
    N: int = 500
    q: float = 0.0
    tipo: str = "call"
    americana: bool = False

    def price(self) -> float:
        import numpy as np
        dt = self.T / self.N
        u = math.exp(self.sigma * math.sqrt(dt))
        d = 1.0 / u
        disc = math.exp(-self.r * dt)
        p = (math.exp((self.r - self.q) * dt) - d) / (u - d)
        if not (0.0 < p < 1.0):
            raise ValueError("Probabilidad neutral al riesgo fuera de (0,1): revisa parámetros")
        j = np.arange(self.N + 1)
        ST = self.S * u ** j * d ** (self.N - j)
        sign = 1.0 if self.tipo == "call" else -1.0
        V = np.maximum(sign * (ST - self.K), 0.0)
        for i in range(self.N, 0, -1):
            V = disc * (p * V[1:i + 1] + (1 - p) * V[0:i])
            if self.americana:
                j = np.arange(i)
                St = self.S * u ** j * d ** (i - 1 - j)
                V = np.maximum(V, sign * (St - self.K))
        return float(V[0])

    def lattice(self):
        """Árboles para inspección/visualización: precios del subyacente (S), valores de la
        opción (V) e indicador de ejercicio óptimo (E, solo americana). Listas jaggeadas
        S[i][j], i=paso (0..N), j=nº de subidas (0..i)."""
        dt = self.T / self.N
        u = math.exp(self.sigma * math.sqrt(dt)); d = 1.0 / u
        disc = math.exp(-self.r * dt)
        p = (math.exp((self.r - self.q) * dt) - d) / (u - d)
        sign = 1.0 if self.tipo == "call" else -1.0
        S = [[self.S * (u ** j) * (d ** (i - j)) for j in range(i + 1)] for i in range(self.N + 1)]
        V = [[0.0] * (i + 1) for i in range(self.N + 1)]
        E = [[False] * (i + 1) for i in range(self.N + 1)]
        for j in range(self.N + 1):
            V[self.N][j] = max(sign * (S[self.N][j] - self.K), 0.0)
        for i in range(self.N - 1, -1, -1):
            for j in range(i + 1):
                cont = disc * (p * V[i + 1][j + 1] + (1 - p) * V[i + 1][j])
                ej = max(sign * (S[i][j] - self.K), 0.0)
                if self.americana and ej > cont:
                    V[i][j] = ej; E[i][j] = True
                else:
                    V[i][j] = cont
        return {"S": S, "V": V, "E": E, "u": u, "d": d, "p": p}


@dataclass
class MonteCarlo:
    """Valuación por simulación Monte Carlo bajo GBM (medida neutral al riesgo).
    Para opciones EUROPEAS. price() devuelve (precio, error_estándar)."""
    S: float
    K: float
    r: float
    sigma: float
    T: float
    q: float = 0.0
    tipo: str = "call"
    m: int = 100_000
    seed: int = 42
    antithetic: bool = True

    def price(self):
        import numpy as np
        rng = np.random.default_rng(self.seed)
        n = self.m // 2 if self.antithetic else self.m
        Z = rng.standard_normal(n)
        if self.antithetic:
            Z = np.concatenate([Z, -Z])
        drift = (self.r - self.q - 0.5 * self.sigma ** 2) * self.T
        ST = self.S * np.exp(drift + self.sigma * math.sqrt(self.T) * Z)
        sign = 1.0 if self.tipo == "call" else -1.0
        payoff = np.maximum(sign * (ST - self.K), 0.0) * math.exp(-self.r * self.T)
        return float(payoff.mean()), float(payoff.std(ddof=1) / math.sqrt(len(payoff)))

    def paths(self, n_paths=50, n_steps=100):
        """Trayectorias GBM completas (n_paths x n_steps+1) para graficar."""
        import numpy as np
        rng = np.random.default_rng(self.seed)
        dt = self.T / n_steps
        incr = ((self.r - self.q - 0.5 * self.sigma ** 2) * dt
                + self.sigma * math.sqrt(dt) * rng.standard_normal((n_paths, n_steps)))
        logS = math.log(self.S) + np.cumsum(incr, axis=1)
        return np.concatenate([np.full((n_paths, 1), self.S), np.exp(logS)], axis=1)


@dataclass
class LongstaffSchwartz:
    """Valuación de opciones AMERICANAS por mínimos cuadrados (Longstaff-Schwartz, 2001):
    Monte Carlo + regresión para estimar el valor de continuación. Funciones base:
    polinomios ordinarios de grado `deg` (recomendación de Stentoft, 2004)."""
    S: float
    K: float
    r: float
    sigma: float
    T: float
    q: float = 0.0
    tipo: str = "put"
    m: int = 100_000
    n_steps: int = 50
    deg: int = 3
    seed: int = 42
    antithetic: bool = True

    def price(self):
        import numpy as np
        rng = np.random.default_rng(self.seed)
        dt = self.T / self.n_steps
        df = math.exp(-self.r * dt)
        n = self.m // 2 if self.antithetic else self.m
        Z = rng.standard_normal((n, self.n_steps))
        if self.antithetic:
            Z = np.vstack([Z, -Z])
        logret = (self.r - self.q - 0.5 * self.sigma ** 2) * dt + self.sigma * math.sqrt(dt) * Z
        paths = self.S * np.exp(np.cumsum(logret, axis=1))   # M x n_steps (t_1..t_N)
        sign = 1.0 if self.tipo == "call" else -1.0
        payoff = np.maximum(sign * (paths - self.K), 0.0)
        cf = payoff[:, -1].copy()                            # flujo al vencimiento
        for t in range(self.n_steps - 2, -1, -1):
            cf *= df                                         # traer el flujo futuro a t
            itm = payoff[:, t] > 0
            if itm.sum() >= self.deg + 1:
                coef = np.polyfit(paths[itm, t], cf[itm], self.deg)
                cont = np.polyval(coef, paths[itm, t])
                ex = payoff[itm, t] > cont                   # ejercer si conviene
                idx = np.where(itm)[0][ex]
                cf[idx] = payoff[idx, t]
        cf *= df                                             # de t_1 a t_0
        return float(cf.mean()), float(cf.std(ddof=1) / math.sqrt(len(cf)))


def _simular_paths(S, r, sigma, T, q, m, n_steps, seed, antithetic=True):
    """Trayectorias GBM (M x n_steps+1, incluye t0) para opciones dependientes de trayectoria."""
    import numpy as np
    rng = np.random.default_rng(seed)
    dt = T / n_steps
    n = m // 2 if antithetic else m
    Z = rng.standard_normal((n, n_steps))
    if antithetic:
        Z = np.vstack([Z, -Z])
    incr = (r - q - 0.5 * sigma ** 2) * dt + sigma * math.sqrt(dt) * Z
    logS = math.log(S) + np.cumsum(incr, axis=1)
    paths = np.exp(logS)
    return np.concatenate([np.full((paths.shape[0], 1), S), paths], axis=1)


def precio_asiatica(S, K, r, sigma, T, q=0.0, tipo="call", m=100_000, n_steps=50, seed=42):
    """Opción ASIÁTICA de promedio aritmético (pago sobre el promedio del precio)."""
    import numpy as np
    paths = _simular_paths(S, r, sigma, T, q, m, n_steps, seed)
    prom = paths[:, 1:].mean(axis=1)
    sign = 1.0 if tipo == "call" else -1.0
    pay = np.maximum(sign * (prom - K), 0.0) * math.exp(-r * T)
    return float(pay.mean()), float(pay.std(ddof=1) / math.sqrt(len(pay)))


def precio_barrera(S, K, r, sigma, T, barrera, q=0.0, tipo="call", tipo_barrera="up-and-out",
                   m=100_000, n_steps=100, seed=42):
    """Opción BARRERA (knock-out): se extingue si el precio toca la barrera."""
    import numpy as np
    paths = _simular_paths(S, r, sigma, T, q, m, n_steps, seed)
    if "up" in tipo_barrera:
        vivo = paths.max(axis=1) < barrera
    else:
        vivo = paths.min(axis=1) > barrera
    sign = 1.0 if tipo == "call" else -1.0
    pay = np.maximum(sign * (paths[:, -1] - K), 0.0) * vivo * math.exp(-r * T)
    return float(pay.mean()), float(pay.std(ddof=1) / math.sqrt(len(pay)))


if __name__ == "__main__":
    # --- Auto-test de robustez ---
    print("== Auto-test opciones.py ==")
    S, K, r, sig, T, q = 100, 100, 0.05, 0.20, 1.0, 0.0
    c = BlackScholes(S, K, r, sig, T, q, "call").price()
    p = BlackScholes(S, K, r, sig, T, q, "put").price()
    # 1) Paridad put-call: C - P = S e^{-qT} - K e^{-rT}
    lhs = c - p
    rhs = S * math.exp(-q * T) - K * math.exp(-r * T)
    print(f"Call={c:.4f}  Put={p:.4f}")
    print(f"Paridad put-call: C-P={lhs:.6f}  S-Ke^-rT={rhs:.6f}  dif={abs(lhs-rhs):.2e}")
    assert abs(lhs - rhs) < 1e-6, "Falla paridad put-call"
    # 2) Binomial europea converge a BSM
    cb = BinomialTree(S, K, r, sig, T, N=2000, tipo="call").price()
    print(f"Binomial europea (N=2000)={cb:.4f}  BSM={c:.4f}  dif={abs(cb-c):.2e}")
    assert abs(cb - c) < 1e-2, "Binomial no converge a BSM"
    # 3) Put americana >= put europea
    pa = BinomialTree(S, K, r, sig, T, N=1000, tipo="put", americana=True).price()
    print(f"Put americana={pa:.4f} >= Put europea={p:.4f}  -> {'OK' if pa >= p - 1e-9 else 'FALLA'}")
    assert pa >= p - 1e-9
    # 4) Vol implícita recupera sigma
    iv = BlackScholes(S, K, r, 0.5, T, q, "call").implied_vol(c)
    print(f"Vol implícita recuperada={iv:.4f}  (real={sig})  dif={abs(iv-sig):.2e}")
    assert abs(iv - sig) < 1e-4
    print("TODOS LOS TESTS PASARON OK")
