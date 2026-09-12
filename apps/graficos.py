"""Cálculos y figuras (matplotlib puro, sin Streamlit) para los dashboards.

Separar las figuras de la interfaz permite renderizarlas y revisarlas fuera de
Streamlit y reutilizarlas en el manuscrito.

Unidades (convención de mercado): volatilidad y tasa se muestran en % anual; vega y rho
por 1 punto porcentual; theta por día calendario. Internamente los motores de
`opciones.py` trabajan en decimales y años."""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from opciones import BlackScholes, BinomialTree, LongstaffSchwartz
from tema import paleta, color_tipo, cmap, figura, linea_referencia, marcador

GRIEGAS = {"price": "Precio", "delta": "Delta Δ", "gamma": "Gamma Γ",
           "vega": "Vega ν (por 1 pt de vol)", "theta": "Theta Θ (por día)",
           "rho": "Rho ρ (por 1 pt de tasa)"}
_ESCALA = {"vega": 1 / 100, "rho": 1 / 100, "theta": 1 / 365}
_PARES = ("delta", "gamma", "vega", "theta")
MOTORES = {"BSM": "Black-Scholes-Merton (europea)",
           "CRR": "Binomial CRR (americana, N = 300)",
           "LSM": "Longstaff-Schwartz (americana, 10 000 trayectorias)"}


def _griega(op, g):
    return getattr(op, g)() * _ESCALA.get(g, 1.0)


def _bsm(S, K, r, sig, T, tipo):
    return BlackScholes(S, K, r, sig, T, tipo=tipo).price()


def _N(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _cotas(S, K, r, T, tipo):
    """Límites de no arbitraje del precio (sin dividendos)."""
    kd = K * math.exp(-r * T)
    return (max(S - kd, 0.0), S) if tipo == "call" else (max(kd - S, 0.0), kd)


def _biseccion(f, lo, hi, tol=1e-9, itmax=200):
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return np.nan
    for _ in range(itmax):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) < tol:
            return mid
        if (fm > 0) == (fhi > 0):
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def etiqueta_plazo(T):
    return f"{T * 365:.0f} d" if T < 45 / 365 else f"{T:.2f} a"


# ----------------------------------------------------------------------------- cálculos

def rango_spot(K, n=200):
    return np.linspace(max(0.01, K * 0.4), K * 1.8, n)


def griegas_actuales(S, K, r, sig, T, tipo):
    op = BlackScholes(S, K, r, sig, T, tipo=tipo)
    return {g: _griega(op, g) for g in GRIEGAS}


def curva_metrica(Sx, K, r, sig, T, tipo, metrica):
    return np.array([_griega(BlackScholes(s, K, r, sig, T, tipo=tipo), metrica) for s in Sx])


def curvas_griegas(K, r, sig, T, n=200):
    """Delta, gamma, vega y theta de call y put a lo largo del spot (BSM)."""
    Sx = rango_spot(K, n)
    out = {}
    for t in ("call", "put"):
        ops = [BlackScholes(s, K, r, sig, T, tipo=t) for s in Sx]
        out[t] = {g: np.array([_griega(o, g) for o in ops]) for g in _PARES}
    return Sx, out


def lectura_mercado(S, K, r, sig, T, tipo):
    """Lo que un operador lee antes de la griega: prob. de terminar ITM (riesgo neutral),
    movimiento esperado ±1σ al vencimiento y punto de equilibrio."""
    prima = _bsm(S, K, r, sig, T, tipo)
    d2 = (math.log(S / K) + (r - 0.5 * sig ** 2) * T) / (sig * math.sqrt(T))
    p_itm = _N(d2) if tipo == "call" else _N(-d2)
    mov = S * sig * math.sqrt(T)
    equilibrio = K + prima if tipo == "call" else K - prima
    return {"prima": prima, "p_itm": p_itm, "mov_1s": mov, "equilibrio": equilibrio,
            "S_lo": S * math.exp(-sig * math.sqrt(T)), "S_hi": S * math.exp(sig * math.sqrt(T))}


def payoff_y_valor(S, K, r, sig, T, tipo, n=241):
    """P&L al vencimiento, hoy y a mitad de camino, comprando la opción al precio BSM."""
    prima = _bsm(S, K, r, sig, T, tipo)
    ancho = 3 * sig * math.sqrt(T)
    Sx = np.linspace(S * math.exp(-ancho), S * math.exp(ancho), n)
    intrinseco = np.maximum(Sx - K, 0) if tipo == "call" else np.maximum(K - Sx, 0)
    hoy = np.array([_bsm(s, K, r, sig, T, tipo) for s in Sx])
    mitad = np.array([_bsm(s, K, r, sig, T / 2, tipo) for s in Sx])
    return {"Sx": Sx, "prima": prima, "vencimiento": intrinseco - prima,
            "hoy": hoy - prima, "mitad": mitad - prima}


def escaleras_griegas(S, K, r, sig, T, tipo):
    """Delta, gamma, vega y theta vs. spot para varios vencimientos (la 'escalera')."""
    vencs = sorted({round(v, 6) for v in (7 / 365, T / 4, T / 2, T) if v > 0})
    Sx = rango_spot(K)
    data = {g: [] for g in _PARES}
    for v in vencs:
        ops = [BlackScholes(s, K, r, sig, v, tipo=tipo) for s in Sx]
        for g in _PARES:
            data[g].append(np.array([_griega(o, g) for o in ops]))
    return Sx, vencs, data


def cadena_opciones(S, K, r, sig, T, n=11):
    """Cadena de opciones estilo monitor: call y put lado a lado por strike (BSM)."""
    paso = max(round(S * 0.025, 2), 0.01)
    centro = round(K / paso) * paso
    strikes = centro + paso * np.arange(-(n // 2), n // 2 + 1)
    strikes = strikes[strikes > 0]
    filas = []
    for k in strikes:
        c = BlackScholes(S, k, r, sig, T, tipo="call")
        p = BlackScholes(S, k, r, sig, T, tipo="put")
        filas.append({"Call": c.price(), "Δ call": c.delta(), "Θ call": _griega(c, "theta"),
                      "Γ": c.gamma(), "ν": _griega(c, "vega"), "Strike": k,
                      "Put": p.price(), "Δ put": p.delta(), "Θ put": _griega(p, "theta")})
    return pd.DataFrame(filas)


def frontera_ejercicio(S, K, r, sig, T, tipo, N=600):
    """Frontera de ejercicio óptimo S*(t) de la opción americana en un árbol CRR.
    Para el put: por debajo de S* conviene ejercer. Para un call sin dividendos no hay
    ejercicio temprano y se devuelve None. En cada fecha la frontera se estima como el
    punto medio entre el nodo más alto que ejerce y el siguiente que espera, lo que
    suaviza la escalera de la malla."""
    if tipo == "call":
        return None
    dt = T / N
    u = math.exp(sig * math.sqrt(dt))
    d = 1 / u
    p = (math.exp(r * dt) - d) / (u - d)
    disc = math.exp(-r * dt)
    j = np.arange(N + 1)
    S_N = S * u ** j * d ** (N - j)
    V = np.maximum(K - S_N, 0.0)
    frontera = np.full(N + 1, np.nan)
    frontera[N] = K
    for i in range(N - 1, -1, -1):
        S_i = S * u ** j[: i + 1] * d ** (i - j[: i + 1])
        cont = disc * (p * V[1: i + 2] + (1 - p) * V[: i + 1])
        intr = np.maximum(K - S_i, 0.0)
        ejercer = intr > cont + 1e-10
        if ejercer.any():
            s_ej = S_i[ejercer].max()
            arriba = S_i[(~ejercer) & (S_i > s_ej)]
            frontera[i] = 0.5 * (s_ej + arriba.min()) if arriba.size else s_ej
        V = np.maximum(cont, intr)
    return np.arange(N + 1) * dt, frontera


def convergencia_crr(S, K, r, sig, T, tipo, Ns=(5, 10, 20, 35, 50, 75, 100, 150, 200, 300, 500, 750, 1000)):
    amer = [BinomialTree(S, K, r, sig, T, N=n, tipo=tipo, americana=True).price() for n in Ns]
    euro = [BinomialTree(S, K, r, sig, T, N=n, tipo=tipo, americana=False).price() for n in Ns]
    return np.array(Ns), np.array(amer), np.array(euro), _bsm(S, K, r, sig, T, tipo)


def convergencia_lsm(S, K, r, sig, T, tipo, ms=(2_000, 5_000, 10_000, 20_000, 40_000, 80_000)):
    res = [LongstaffSchwartz(S, K, r, sig, T, tipo=tipo, m=m, n_steps=50).price() for m in ms]
    ref = BinomialTree(S, K, r, sig, T, N=1200, tipo=tipo, americana=True).price()
    return np.array(ms), np.array([x[0] for x in res]), np.array([x[1] for x in res]), ref


def cotizaciones_ejemplo(S, K, r, sig, T, tipo):
    """Cinco cotizaciones sintéticas con skew de renta variable (más vol en strikes bajos),
    para que el lector vea una sonrisa y luego sustituya por precios reales."""
    ks = np.round(K * np.array([0.90, 0.95, 1.00, 1.05, 1.10]), 2)
    filas = []
    for k in ks:
        m = k / S - 1
        s_k = max(0.05, sig - 0.35 * m + 0.9 * m ** 2)
        filas.append({"Strike": float(k), "Precio de mercado": round(_bsm(S, k, r, s_k, T, tipo), 4)})
    return pd.DataFrame(filas)


def sonrisa(S, r, T, tipo, cotizaciones):
    """Vol implícita (%) por strike a partir de precios observados; NaN si el precio viola
    las cotas de no arbitraje."""
    out = []
    for _, fila in cotizaciones.iterrows():
        k, p = float(fila["Strike"]), float(fila["Precio de mercado"])
        lb, ub = _cotas(S, k, r, T, tipo)
        iv = np.nan
        if k > 0 and lb + 1e-9 < p < ub - 1e-9:
            iv = BlackScholes(S, k, r, 0.2, T, tipo=tipo).implied_vol(p) * 100
            if iv > 400:
                iv = np.nan
        out.append(iv)
    df = cotizaciones.copy()
    df["Vol implícita (%)"] = out
    return df.sort_values("Strike")


def matriz_sensibilidad(metrica, S, K, r, sig, T, tipo, n=11):
    """La 'matriz de sensibilidad' clásica: métrica en spot × volatilidad (filas = σ, en %)."""
    Ss = np.linspace(S * 0.8, S * 1.2, n)
    sigs = np.linspace(max(0.02, sig - 0.10), sig + 0.10, n)
    grid = np.array([[_griega(BlackScholes(s, K, r, ss, T, tipo=tipo), metrica) for s in Ss]
                     for ss in sigs])
    return Ss, sigs * 100, grid


def mapa_americano(S, K, r, sig, T, tipo, n=9, N=200):
    """Precio americano (CRR) y europeo (BSM) en spot × vencimiento (filas = T)."""
    Ss = np.linspace(S * 0.7, S * 1.3, n)
    Ts = np.linspace(max(0.05, T * 0.25), T * 1.75, n)
    amer = np.array([[BinomialTree(s, K, r, sig, tt, N=N, tipo=tipo, americana=True).price()
                      for s in Ss] for tt in Ts])
    euro = np.array([[_bsm(s, K, r, sig, tt, tipo) for s in Ss] for tt in Ts])
    return Ss, Ts, amer, euro


def mapa_sigma_r(S, K, r, sig, T, tipo, motor, n=9):
    """Precio en volatilidad × tasa (ambas en %) con el motor elegido (filas = r)."""
    if motor == "LSM":
        n = 7
    sigs = np.linspace(max(0.05, sig - 0.15), sig + 0.15, n)
    rs = np.linspace(max(0.0, r - 0.04), r + 0.04, n)

    def precio(ss, rr):
        if motor == "BSM":
            return _bsm(S, K, rr, ss, T, tipo)
        if motor == "CRR":
            return BinomialTree(S, K, rr, ss, T, N=300, tipo=tipo, americana=True).price()
        return LongstaffSchwartz(S, K, rr, ss, T, tipo=tipo, m=10_000, n_steps=50).price()[0]

    grid = np.array([[precio(ss, rr) for ss in sigs] for rr in rs])
    return sigs * 100, rs * 100, grid


def mapa_vol_implicita(S, K, r, T, tipo, n=9):
    """Vol implícita (%) en strike × precio de la opción. Celdas sin solución = NaN.
    El rango de precios es el que producen vols de 8 % a 70 % en el strike central."""
    Ks = np.linspace(K * 0.85, K * 1.15, n)
    p_lo, p_hi = sorted((_bsm(S, K, r, 0.08, T, tipo), _bsm(S, K, r, 0.70, T, tipo)))
    Ps = np.linspace(p_lo, p_hi, n)
    grid = np.full((n, n), np.nan)
    for j, k in enumerate(Ks):
        lb, ub = _cotas(S, k, r, T, tipo)
        for i, p in enumerate(Ps):
            if lb + 1e-9 < p < ub - 1e-9:
                iv = BlackScholes(S, k, r, 0.2, T, tipo=tipo).implied_vol(p)
                if iv < 4.0:
                    grid[i, j] = iv * 100
    return Ks, Ps, grid


def mapa_tasa_implicita(S, K, sig, T, tipo, n=9, r_lo=-0.10, r_hi=0.60):
    """Tasa implícita (%) en strike × precio de la opción, dada la volatilidad."""
    Ks = np.linspace(K * 0.85, K * 1.15, n)
    p_lo, p_hi = sorted((_bsm(S, K, r_lo, sig, T, tipo), _bsm(S, K, r_hi, sig, T, tipo)))
    Ps = np.linspace(p_lo, p_hi, n)
    grid = np.full((n, n), np.nan)
    for j, k in enumerate(Ks):
        for i, p in enumerate(Ps):
            rr = _biseccion(lambda x: _bsm(S, k, x, sig, T, tipo) - p, r_lo, r_hi)
            if not np.isnan(rr):
                grid[i, j] = rr * 100
    return Ks, Ps, grid


# ------------------------------------------------------------------------------ figuras

def fig_payoff(modo, d, S, K, T, tipo, lectura):
    """Diagrama de P&L: al vencimiento (con zonas de ganancia/pérdida), hoy y a T/2,
    más el cono de ±1σ del subyacente."""
    p = paleta(modo)
    c, e = p["chrome"], p["estado"]
    col = color_tipo(modo, tipo)
    Sx = d["Sx"]
    fig, ax = figura(modo, 9, 4.4)
    ax.fill_between(Sx, d["vencimiento"], 0, where=d["vencimiento"] >= 0,
                    color=e["ganancia"], alpha=0.12, lw=0)
    ax.fill_between(Sx, d["vencimiento"], 0, where=d["vencimiento"] < 0,
                    color=e["perdida"], alpha=0.12, lw=0)
    ax.axvspan(lectura["S_lo"], lectura["S_hi"], color=col, alpha=0.07, lw=0,
               label="±1σ al vencimiento")
    ax.plot(Sx, d["vencimiento"], color=c["secundaria"], lw=1.8, label="al vencimiento")
    ax.plot(Sx, d["mitad"], color=col, lw=1.5, alpha=0.5, label=f"a T/2 ({etiqueta_plazo(T / 2)})")
    ax.plot(Sx, d["hoy"], color=col, lw=2.2, label="hoy")
    ax.axhline(0, color=c["eje"], lw=0.8)
    linea_referencia(ax, modo, K, f"K = {K:g}")
    marcador(ax, modo, S, 0.0, col)
    ax.annotate(f"S = {S:g}", xy=(S, 0), xytext=(8, 8), textcoords="offset points",
                fontsize=9, color=c["tinta"])
    eq = lectura["equilibrio"]
    if Sx[0] < eq < Sx[-1]:
        ax.plot([eq], [0], marker="|", ms=12, color=c["tinta"], mew=1.5)
        ax.annotate(f"equilibrio {eq:.2f}", xy=(eq, 0), xytext=(0, -16), textcoords="offset points",
                    ha="center", fontsize=9, color=c["secundaria"])
    ax.set_title(f"P&L del {tipo} largo comprado a {d['prima']:.4f}")
    ax.set_xlabel("Spot al evaluar")
    ax.set_ylabel("P&L por unidad")
    ax.legend(loc="upper left" if tipo == "call" else "upper right")
    return fig


def fig_escaleras(modo, Sx, vencs, data, S, K, tipo):
    """Cuatro paneles (delta, gamma, vega, theta) vs. spot, una línea por vencimiento."""
    p = paleta(modo)
    c = p["chrome"]
    ord_ = p["ordinal"]
    fig, axes = figura(modo, 11, 6.2, ncols=2, nrows=2)
    for ax, g in zip(axes.ravel(), _PARES):
        for k, (v, y) in enumerate(zip(vencs, data[g])):
            ax.plot(Sx, y, color=ord_[min(k, len(ord_) - 1)], lw=2.0 if k == len(vencs) - 1 else 1.6,
                    label=etiqueta_plazo(v))
        ax.axvline(K, color=c["eje"], lw=1.0)
        ax.axvline(S, color=c["apagada"], lw=0.8)
        if g in ("delta", "theta"):
            ax.axhline(0, color=c["eje"], lw=0.8)
        ax.set_title(GRIEGAS[g])
        ax.set_xlabel("Spot S")
    axes[0, 0].legend(title="vencimiento", loc="best", title_fontsize=9)
    axes[0, 0].annotate("K", xy=(K, 1.0), xycoords=("data", "axes fraction"), xytext=(4, -2),
                        textcoords="offset points", va="top", fontsize=9, color=c["apagada"])
    axes[0, 0].annotate("S", xy=(S, 0.0), xycoords=("data", "axes fraction"), xytext=(4, 2),
                        textcoords="offset points", va="bottom", fontsize=9, color=c["apagada"])
    return fig


def fig_frontera(modo, t, frontera, S, K, T, tipo):
    """Frontera de ejercicio óptimo del put americano: ejercer por debajo, esperar por encima."""
    c = paleta(modo)["chrome"]
    col = color_tipo(modo, tipo)
    fig, ax = figura(modo, 9, 4)
    ok = ~np.isnan(frontera)
    ax.fill_between(t[ok], frontera[ok], np.nanmin(frontera[ok]) * 0.85, color=col, alpha=0.10, lw=0)
    ax.plot(t[ok], frontera[ok], color=col, lw=2.2, label="frontera S*(t)")
    ax.axhline(K, color=c["eje"], lw=1.0)
    ax.annotate(f"K = {K:g}", xy=(t[-1], K), xytext=(-4, 4), textcoords="offset points",
                ha="right", fontsize=9, color=c["apagada"])
    marcador(ax, modo, 0.0, S, col)
    ax.annotate(f"S hoy = {S:g}", xy=(0, S), xytext=(8, 6), textcoords="offset points",
                fontsize=9, color=c["tinta"])
    ymid = np.nanmin(frontera[ok]) * 0.92
    ax.text(T * 0.05, ymid, "ejercer", fontsize=9, color=c["secundaria"], va="bottom")
    ax.text(T * 0.05, K * 1.005, "esperar", fontsize=9, color=c["secundaria"], va="bottom")
    ax.set_title("Frontera de ejercicio óptimo del put americano (CRR)")
    ax.set_xlabel("Tiempo transcurrido (años)")
    ax.set_ylabel("Spot")
    ax.set_xlim(0, T)
    ax.legend(loc="lower right")
    return fig


def fig_convergencia(modo, Ns, crr_amer, crr_euro, bsm, ms, lsm, se, ref, tipo):
    """Izquierda: CRR contra N (europea y americana), con BSM de referencia.
    Derecha: LSM contra trayectorias con banda de ±1.96 errores estándar y CRR de referencia."""
    p = paleta(modo)
    c, s = p["chrome"], p["serie"]
    col = color_tipo(modo, tipo)
    fig, (a1, a2) = figura(modo, 11, 4, ncols=2)
    a1.axhline(bsm, color=c["eje"], lw=1.2)
    a1.annotate(f"BSM europea {bsm:.4f}", xy=(Ns[0], bsm), xytext=(4, -12), textcoords="offset points",
                ha="left", fontsize=9, color=c["apagada"])
    a1.plot(Ns, crr_euro, color=s["verde"], lw=1.8, marker="o", ms=5, label="CRR europea")
    a1.plot(Ns, crr_amer, color=col, lw=2.2, marker="o", ms=5, label="CRR americana")
    a1.set_xscale("log")
    a1.set_title("Binomial CRR: precio vs. pasos N")
    a1.set_xlabel("N (escala log)")
    a1.set_ylabel("Precio")
    a1.legend(loc="best")
    a2.axhline(ref, color=c["eje"], lw=1.2)
    a2.annotate(f"CRR N = 1200: {ref:.4f}", xy=(ms[0], ref), xytext=(4, -12), textcoords="offset points",
                ha="left", fontsize=9, color=c["apagada"])
    a2.fill_between(ms, lsm - 1.96 * se, lsm + 1.96 * se, color=s["verde"], alpha=0.15, lw=0,
                    label="±1.96 error estándar")
    a2.plot(ms, lsm, color=s["verde"], lw=2.2, marker="o", ms=5, label="LSM americana")
    a2.set_xscale("log")
    a2.set_title("Longstaff-Schwartz: precio vs. trayectorias")
    a2.set_xlabel("Trayectorias (escala log)")
    a2.legend(loc="best")
    return fig


def fig_sonrisa(modo, df, sig, K, tipo):
    """Sonrisa de volatilidad implícita por strike, con la vol plana del modelo de referencia."""
    c = paleta(modo)["chrome"]
    col = color_tipo(modo, tipo)
    fig, ax = figura(modo, 8, 4.2)
    ok = df["Vol implícita (%)"].notna()
    ax.axhline(sig * 100, color=c["eje"], lw=1.2)
    ax.annotate(f"σ del modelo {sig * 100:.0f} %", xy=(df["Strike"].max(), sig * 100), xytext=(-4, 4),
                textcoords="offset points", ha="right", fontsize=9, color=c["apagada"])
    ax.plot(df.loc[ok, "Strike"], df.loc[ok, "Vol implícita (%)"], color=col, lw=2.0, marker="o", ms=8,
            markeredgecolor=c["superficie"], markeredgewidth=2, label="vol implícita")
    linea_referencia(ax, modo, K, f"K = {K:g}")
    ax.set_title(f"Sonrisa de volatilidad implícita del {tipo}")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Vol implícita (% anual)")
    return fig


def fig_curva_spot(modo, Sx, y, tipo, y_otro, S, y_S, K, metrica):
    """Curva de una métrica vs. spot; la opción contraria se dibuja recesiva."""
    c = paleta(modo)["chrome"]
    otro = "put" if tipo == "call" else "call"
    fig, ax = figura(modo, 9, 4)
    if y_otro is not None:
        ax.plot(Sx, y_otro, color=color_tipo(modo, otro), lw=1.6, alpha=0.55, label=otro)
    ax.plot(Sx, y, color=color_tipo(modo, tipo), lw=2.2, label=tipo)
    marcador(ax, modo, S, y_S, color_tipo(modo, tipo))
    ax.annotate(f"S = {S:g}", xy=(S, y_S), xytext=(8, 8), textcoords="offset points",
                fontsize=9, color=c["tinta"])
    ax.axhline(0, color=c["eje"], lw=0.8)
    linea_referencia(ax, modo, K, f"K = {K:g}")
    ax.set_title(f"{GRIEGAS[metrica]} en función del spot")
    ax.set_xlabel("Spot S")
    ax.set_ylabel(GRIEGAS[metrica])
    if y_otro is not None:
        ax.legend(loc="best")
    return fig


def fig_pares_griegas(modo, curvas, actual, tipo):
    """Los tres pares del analista: gamma, vega y theta contra delta (delta ≈ moneyness)."""
    c = paleta(modo)["chrome"]
    fig, axes = figura(modo, 11, 3.6, ncols=3)
    titulos = {"gamma": "Gamma vs. delta", "vega": "Vega vs. delta", "theta": "Theta vs. delta"}
    for ax, g in zip(axes, ("gamma", "vega", "theta")):
        for t in ("call", "put"):
            ax.plot(curvas[t]["delta"], curvas[t][g], color=color_tipo(modo, t),
                    lw=2.0 if t == tipo else 1.4, alpha=1.0 if t == tipo else 0.55, label=t)
        marcador(ax, modo, actual["delta"], actual[g], color_tipo(modo, tipo))
        ax.axvline(0, color=c["eje"], lw=0.8)
        if g == "theta":
            ax.axhline(0, color=c["eje"], lw=0.8)
        ax.set_title(titulos[g])
        ax.set_xlabel("Delta Δ")
        ax.set_ylabel(GRIEGAS[g])
        ax.set_xlim(-1.02, 1.02)
    axes[0].legend(loc="lower center", ncols=2)
    return fig


def fig_mapa(modo, grid, xs, ys, xlabel, ylabel, titulo, punto, etiqueta_cb, color_punto,
             etiqueta_punto="configuración actual"):
    """Mapa de calor de una magnitud (rampa monocroma) con el punto de configuración actual.
    Las celdas NaN (sin solución) se dejan del color de la superficie."""
    c = paleta(modo)["chrome"]
    fig, ax = figura(modo, 8, 4.2)
    ax.grid(False)
    cm = cmap(modo)
    cm.set_bad(c["superficie"])
    dx = (xs[-1] - xs[0]) / (2 * (len(xs) - 1))
    dy = (ys[-1] - ys[0]) / (2 * (len(ys) - 1))
    im = ax.imshow(np.ma.masked_invalid(grid), aspect="auto", origin="lower", cmap=cm,
                   extent=[xs[0] - dx, xs[-1] + dx, ys[0] - dy, ys[-1] + dy],
                   interpolation="nearest")
    if punto is not None:
        marcador(ax, modo, punto[0], punto[1], color_punto)
        ax.annotate(etiqueta_punto, xy=punto, xytext=(9, 9), textcoords="offset points",
                    fontsize=9, color=c["tinta"],
                    bbox=dict(boxstyle="round,pad=0.25", fc=c["superficie"], ec="none", alpha=0.85))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    cb = fig.colorbar(im, ax=ax, pad=0.02)
    cb.set_label(etiqueta_cb, color=c["secundaria"])
    cb.outline.set_visible(False)
    cb.ax.tick_params(color=c["apagada"], labelcolor=c["apagada"], labelsize=9)
    return fig
