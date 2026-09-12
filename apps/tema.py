"""Paleta y estilo visual compartido de los dashboards del libro.

Cada color hace un solo trabajo:
  - SERIE:   identidad (call, put, motor de valuación). Orden fijo; el color sigue a la
             entidad, no a la posición: un call siempre es azul, un put siempre naranja.
  - ORDINAL: posición en una secuencia (vencimientos). Un solo tono en pasos de luminosidad.
  - RAMPA:   magnitud (mapas de calor). Un solo tono, del más cercano a la superficie al
             más lejano; por eso se invierte entre modo claro y oscuro.
  - ESTADO:  ganancia / pérdida en diagramas de P&L. Reservados; nunca como serie.
  - CHROME:  superficie, tinta, ejes, rejilla y acento de interfaz. Recesivo.

Modo oscuro: superficie casi negra y acento ámbar, el lenguaje visual de las terminales
financieras; los datos usan las series validadas. Ambos modos pasaron los seis chequeos
del método de visualización: banda de luminosidad OKLCH, piso de croma, separación bajo
protanopia/deuteranopia simuladas (Machado, Oliveira y Fernandes, 2009), piso de visión
normal y contraste WCAG.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

_RAMPA_AZUL = ["#e2e8f2", "#bfd0ed", "#9db7e6", "#7b9fde", "#5a86d6",
               "#396ccd", "#2255b4", "#144093", "#072c72"]

MODOS = {
    "light": {
        "serie":   {"azul": "#2B62C9", "naranja": "#E0702E", "verde": "#0F9E86",
                    "violeta": "#7A55D1", "oro": "#B8860B"},
        "ordinal": ["#7b9fde", "#5a86d6", "#396ccd", "#2255b4"],
        "estado":  {"ganancia": "#1B8F4E", "perdida": "#C93B3B"},
        "chrome":  {"superficie": "#FCFCFB", "plano": "#F3F3EF", "tinta": "#0B0B0B",
                    "secundaria": "#52514E", "apagada": "#898781",
                    "rejilla": "#E1E0D9", "eje": "#C3C2B7", "acento": "#2B62C9"},
        "rampa":   _RAMPA_AZUL,
        "streamlit": {"base": "light", "primaryColor": "#2B62C9",
                      "backgroundColor": "#FCFCFB", "secondaryBackgroundColor": "#F3F3EF",
                      "textColor": "#0B0B0B", "linkColor": "#2B62C9",
                      "borderColor": "#E1E0D9",
                      "chartCategoricalColors": ["#2B62C9", "#E0702E", "#0F9E86", "#7A55D1", "#B8860B"],
                      "chartSequentialColors": _RAMPA_AZUL},
    },
    "dark": {
        "serie":   {"azul": "#3A74DC", "naranja": "#E0702E", "verde": "#0F9E86",
                    "violeta": "#8462D6", "oro": "#B8860B"},
        "ordinal": ["#9db7e6", "#7b9fde", "#5a86d6", "#396ccd"],
        "estado":  {"ganancia": "#22B573", "perdida": "#E5484D"},
        "chrome":  {"superficie": "#0E1117", "plano": "#161B22", "tinta": "#F3F4F6",
                    "secundaria": "#C3C7CE", "apagada": "#8B919A",
                    "rejilla": "#262C36", "eje": "#3A414D", "acento": "#F5A623"},
        "rampa":   _RAMPA_AZUL[::-1],
        "streamlit": {"base": "dark", "primaryColor": "#F5A623",
                      "backgroundColor": "#0E1117", "secondaryBackgroundColor": "#161B22",
                      "textColor": "#F3F4F6", "linkColor": "#7FA6F0",
                      "borderColor": "#262C36",
                      "chartCategoricalColors": ["#3A74DC", "#E0702E", "#0F9E86", "#8462D6", "#B8860B"],
                      "chartSequentialColors": _RAMPA_AZUL[::-1]},
    },
}


def paleta(modo: str) -> dict:
    return MODOS.get(modo, MODOS["dark"])


def color_tipo(modo: str, tipo: str) -> str:
    """Color por entidad: call -> azul, put -> naranja (en ambos modos)."""
    s = paleta(modo)["serie"]
    return s["azul"] if tipo == "call" else s["naranja"]


def color_motor(modo: str, motor: str) -> str:
    s = paleta(modo)["serie"]
    return {"BSM": s["azul"], "CRR": s["naranja"], "LSM": s["verde"]}[motor]


def cmap(modo: str) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(f"azul_libro_{modo}", paleta(modo)["rampa"])


def aplicar_estilo(modo: str) -> None:
    """Estilo del libro en matplotlib: marcas finas, rejilla hairline, ejes recesivos."""
    p = paleta(modo)
    c = p["chrome"]
    mpl.rcParams.update({
        "figure.facecolor":  c["superficie"],
        "axes.facecolor":    c["superficie"],
        "savefig.facecolor": c["superficie"],
        "axes.edgecolor":    c["eje"],
        "axes.linewidth":    0.8,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.labelcolor":   c["secundaria"],
        "axes.titlecolor":   c["tinta"],
        "axes.titlesize":    11.5,
        "axes.titleweight":  "600",
        "axes.titlelocation": "left",
        "axes.grid":         True,
        "axes.axisbelow":    True,
        "grid.color":        c["rejilla"],
        "grid.linewidth":    0.8,
        "grid.linestyle":    "-",
        "xtick.color":       c["apagada"],
        "ytick.color":       c["apagada"],
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "text.color":        c["tinta"],
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Segoe UI", "DejaVu Sans", "Arial", "sans-serif"],
        "font.size":         10,
        "lines.linewidth":   2.0,
        "lines.solid_capstyle":  "round",
        "lines.solid_joinstyle": "round",
        "legend.frameon":    False,
        "legend.fontsize":   9,
        "legend.labelcolor": c["secundaria"],
        "axes.prop_cycle":   mpl.cycler(color=list(p["serie"].values())),
    })


def figura(modo: str, ancho: float = 9, alto: float = 4, ncols: int = 1, nrows: int = 1):
    aplicar_estilo(modo)
    return plt.subplots(nrows, ncols, figsize=(ancho, alto), layout="constrained")


def linea_referencia(ax, modo: str, x: float, etiqueta: str) -> None:
    """Línea vertical de referencia (p. ej. el strike): hairline sólida en tinta apagada."""
    c = paleta(modo)["chrome"]
    ax.axvline(x, color=c["eje"], lw=1.0, zorder=1)
    ax.annotate(etiqueta, xy=(x, 1.0), xycoords=("data", "axes fraction"),
                xytext=(4, -2), textcoords="offset points",
                ha="left", va="top", fontsize=9, color=c["apagada"])


def marcador(ax, modo: str, x: float, y: float, color: str) -> None:
    """Punto de estado actual: >= 8 px con anillo de 2 px del color de la superficie."""
    c = paleta(modo)["chrome"]
    ax.plot([x], [y], marker="o", ms=9, color=color, ls="none",
            markeredgecolor=c["superficie"], markeredgewidth=2, zorder=6)
